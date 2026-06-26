from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.feature_store.service import FEATURE_VERSION, FeatureStoreService
from app.ml.utils.constants import (
    AGE_GROUP_RANKS,
    FEATURE_DESCRIPTIONS,
    INCOME_CATEGORY_RANKS,
    ML_FEATURE_COLUMNS,
)
from app.models.canonical import Customer, FeatureSnapshot


@dataclass(frozen=True)
class FeatureMatrix:
    customer_ids: list[str]
    frame: pd.DataFrame
    feature_version: str
    dataset_version: str
    feature_descriptions: dict[str, str]


@dataclass(frozen=True)
class RiskTrainingMatrix(FeatureMatrix):
    target: pd.Series


@dataclass(frozen=True)
class CustomerFeatureVector:
    customer_id: str
    frame: pd.DataFrame
    raw_features: dict[str, float]
    feature_descriptions: dict[str, str]
    feature_version: str
    dataset_version: str


class FeatureMatrixBuilder:
    """Builds reusable ML matrices from canonical customers and feature snapshots."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.feature_store = FeatureStoreService(session)

    def build_risk_training_matrix(self) -> RiskTrainingMatrix:
        snapshots = self._latest_snapshots()
        rows = [self._row_from_snapshot(snapshot) for snapshot in snapshots]
        targets = [
            self._risk_label(snapshot.customer, row)
            for snapshot, row in zip(snapshots, rows, strict=True)
        ]
        matrix = self._build_frame(rows)
        return RiskTrainingMatrix(
            customer_ids=[snapshot.customer_id for snapshot in snapshots],
            frame=matrix,
            feature_version=FEATURE_VERSION,
            dataset_version=self._dataset_version(),
            feature_descriptions=dict(FEATURE_DESCRIPTIONS),
            target=pd.Series(targets, name="risk_level"),
        )

    def build_segmentation_matrix(self) -> FeatureMatrix:
        snapshots = self._latest_snapshots()
        rows = [self._row_from_snapshot(snapshot) for snapshot in snapshots]
        return FeatureMatrix(
            customer_ids=[snapshot.customer_id for snapshot in snapshots],
            frame=self._build_frame(rows),
            feature_version=FEATURE_VERSION,
            dataset_version=self._dataset_version(),
            feature_descriptions=dict(FEATURE_DESCRIPTIONS),
        )

    def build_customer_vector(self, customer_id: str) -> CustomerFeatureVector:
        snapshot = self.feature_store.latest_for_customer(customer_id)
        if snapshot is None:
            msg = f"No feature snapshot found for customer {customer_id}"
            raise ValueError(msg)
        row = self._row_from_snapshot(snapshot)
        return CustomerFeatureVector(
            customer_id=customer_id,
            frame=self._build_frame([row]),
            raw_features=row,
            feature_descriptions=dict(FEATURE_DESCRIPTIONS),
            feature_version=snapshot.feature_version,
            dataset_version=snapshot.dataset_version,
        )

    def _latest_snapshots(self) -> list[FeatureSnapshot]:
        dataset_version = self._dataset_version()
        snapshots = list(
            self.session.scalars(
                select(FeatureSnapshot)
                .where(
                    FeatureSnapshot.feature_version == FEATURE_VERSION,
                    FeatureSnapshot.dataset_version == dataset_version,
                )
                .options(
                    selectinload(FeatureSnapshot.customer).selectinload(Customer.loans),
                    selectinload(FeatureSnapshot.customer).selectinload(
                        Customer.products
                    ),
                    selectinload(FeatureSnapshot.customer).selectinload(
                        Customer.transactions
                    ),
                )
                .order_by(FeatureSnapshot.customer_id)
            )
        )
        if not snapshots:
            msg = "No feature snapshots are available. Run Phase 2 ingestion first."
            raise ValueError(msg)
        return snapshots

    def _dataset_version(self) -> str:
        return self.feature_store.current_dataset_version()

    def _build_frame(self, rows: list[dict[str, float]]) -> pd.DataFrame:
        return pd.DataFrame(rows, columns=list(ML_FEATURE_COLUMNS))

    def _row_from_snapshot(self, snapshot: FeatureSnapshot) -> dict[str, float]:
        values = self._dict_value(snapshot.features.get("values"))
        customer = snapshot.customer
        income_category = str(
            values.get("income_category") or customer.income_category or "Unknown"
        )
        age_group = str(values.get("age_group") or "Unknown")
        row = {
            "credit_score": self._numeric(customer.credit_score),
            "estimated_income": self._numeric(customer.estimated_income),
            "savings_balance": self._numeric(customer.savings_balance),
            "age": self._numeric(customer.age),
            "tenure_months": self._numeric(customer.tenure_months),
            "debt_to_income": self._numeric(values.get("debt_to_income")),
            "savings_ratio": self._numeric(values.get("savings_ratio")),
            "spend_ratio": self._numeric(values.get("spend_ratio")),
            "credit_utilization": self._numeric(values.get("credit_utilization")),
            "salary_stability": self._numeric(values.get("salary_stability")),
            "product_count": self._numeric(values.get("product_count")),
            "loan_exposure": self._numeric(values.get("loan_exposure")),
            "average_transaction_amount": self._numeric(
                values.get("average_transaction_amount")
            ),
            "transaction_frequency": self._numeric(values.get("transaction_frequency")),
            "monthly_spending": self._numeric(values.get("monthly_spending")),
            "customer_tenure": self._numeric(values.get("customer_tenure")),
            "risk_indicators": self._numeric(values.get("risk_indicators")),
            "income_category_rank": INCOME_CATEGORY_RANKS.get(income_category, 0.0),
            "age_group_rank": AGE_GROUP_RANKS.get(age_group, 0.0),
        }
        return {key: row[key] for key in ML_FEATURE_COLUMNS}

    def _risk_label(self, customer: Customer, row: dict[str, float]) -> str:
        score = 0
        credit_score = row["credit_score"]
        if credit_score == 0:
            score += 1
        elif credit_score < 580:
            score += 3
        elif credit_score < 650:
            score += 2
        elif credit_score < 700:
            score += 1

        score += self._threshold_score(row["debt_to_income"], (0.5, 1.5, 3.0))
        score += self._inverse_threshold_score(row["savings_ratio"], (0.05, 0.2))
        score += self._threshold_score(row["credit_utilization"], (0.3, 0.6, 0.85))
        score += self._threshold_score(row["spend_ratio"], (0.25, 0.4))
        score += int(row["risk_indicators"])

        if customer.estimated_income is None:
            score += 1
        if any(loan.status.lower() in {"n", "rejected"} for loan in customer.loans):
            score += 2

        if score >= 5:
            return "High"
        if score >= 2:
            return "Medium"
        return "Low"

    def _threshold_score(
        self,
        value: float,
        thresholds: tuple[float, ...],
    ) -> int:
        return sum(1 for threshold in thresholds if value > threshold)

    def _inverse_threshold_score(
        self,
        value: float,
        thresholds: tuple[float, ...],
    ) -> int:
        if value == 0:
            return 1
        return sum(1 for threshold in thresholds if value < threshold)

    def _numeric(self, value: Any) -> float:
        if value is None:
            return 0.0
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _dict_value(self, value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return value
        return {}
