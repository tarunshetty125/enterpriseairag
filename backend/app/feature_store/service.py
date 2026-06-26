from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.datasets.utils import age_group, income_category
from app.models.canonical import Customer, DatasetMetadata, FeatureSnapshot

FEATURE_VERSION = "features_v1"


@dataclass(frozen=True)
class FeatureDefinition:
    name: str
    description: str


FEATURE_DEFINITIONS: tuple[FeatureDefinition, ...] = (
    FeatureDefinition(
        "debt_to_income", "Total outstanding loan exposure divided by income."
    ),
    FeatureDefinition("savings_ratio", "Savings or balance divided by income."),
    FeatureDefinition("spend_ratio", "Estimated monthly spend divided by income."),
    FeatureDefinition(
        "credit_utilization", "Revolving credit balance divided by credit limit."
    ),
    FeatureDefinition(
        "salary_stability", "Heuristic stability score from tenure and income."
    ),
    FeatureDefinition("product_count", "Number of active financial products."),
    FeatureDefinition(
        "loan_exposure", "Total loan amount associated with the customer."
    ),
    FeatureDefinition(
        "average_transaction_amount", "Average amount across linked transactions."
    ),
    FeatureDefinition(
        "transaction_frequency", "Number of transactions linked to the customer."
    ),
    FeatureDefinition("monthly_spending", "Estimated monthly debit spending."),
    FeatureDefinition(
        "income_category", "Income band derived from known income fields."
    ),
    FeatureDefinition("age_group", "Customer age cohort."),
    FeatureDefinition("customer_tenure", "Customer tenure in months."),
    FeatureDefinition(
        "risk_indicators", "Count of deterministic financial risk flags."
    ),
)


class FeatureGenerator:
    """Generates reusable deterministic customer features from canonical records."""

    def generate_for_customer(self, customer: Customer) -> dict[str, Any]:
        income = customer.estimated_income or 0.0
        savings = customer.savings_balance or 0.0
        loan_exposure = sum(loan.amount for loan in customer.loans)
        product_count = len(customer.products)
        credit_limit = sum(product.credit_limit or 0.0 for product in customer.products)
        revolving_balance = sum(
            product.revolving_balance or 0.0 for product in customer.products
        )
        debit_transactions = [
            transaction
            for transaction in customer.transactions
            if transaction.direction == "debit"
        ]
        transaction_amounts = [
            transaction.amount for transaction in customer.transactions
        ]
        total_debit_spend = sum(
            transaction.amount for transaction in debit_transactions
        )
        monthly_spending = (
            round(total_debit_spend / 12, 2) if debit_transactions else 0.0
        )
        average_transaction_amount = (
            round(sum(transaction_amounts) / len(transaction_amounts), 2)
            if transaction_amounts
            else 0.0
        )
        risk_indicators = self._risk_indicators(
            income=income,
            loan_exposure=loan_exposure,
            credit_limit=credit_limit,
            revolving_balance=revolving_balance,
            monthly_spending=monthly_spending,
            credit_score=customer.credit_score,
        )

        return {
            "debt_to_income": self._safe_ratio(loan_exposure, income),
            "savings_ratio": self._safe_ratio(savings, income),
            "spend_ratio": self._safe_ratio(monthly_spending, income),
            "credit_utilization": self._safe_ratio(revolving_balance, credit_limit),
            "salary_stability": self._salary_stability(customer),
            "product_count": product_count,
            "loan_exposure": round(loan_exposure, 2),
            "average_transaction_amount": average_transaction_amount,
            "transaction_frequency": len(customer.transactions),
            "monthly_spending": monthly_spending,
            "income_category": customer.income_category or income_category(income),
            "age_group": age_group(customer.age),
            "customer_tenure": customer.tenure_months or 0,
            "risk_indicators": risk_indicators,
        }

    def describe_features(self) -> dict[str, str]:
        return {
            definition.name: definition.description
            for definition in FEATURE_DEFINITIONS
        }

    def _safe_ratio(self, numerator: float, denominator: float) -> float | None:
        if denominator <= 0:
            return None
        return round(numerator / denominator, 4)

    def _salary_stability(self, customer: Customer) -> float:
        if customer.estimated_income is None:
            return 0.0
        tenure = customer.tenure_months or 0
        if tenure >= 48:
            return 0.95
        if tenure >= 24:
            return 0.85
        if tenure >= 12:
            return 0.75
        return 0.6

    def _risk_indicators(
        self,
        *,
        income: float,
        loan_exposure: float,
        credit_limit: float,
        revolving_balance: float,
        monthly_spending: float,
        credit_score: int | None,
    ) -> int:
        indicators = 0
        if income > 0 and loan_exposure / income > 3:
            indicators += 1
        if credit_limit > 0 and revolving_balance / credit_limit > 0.75:
            indicators += 1
        if income > 0 and monthly_spending / income > 0.4:
            indicators += 1
        if credit_score is not None and credit_score < 600:
            indicators += 1
        return indicators


class FeatureStoreService:
    """Creates and reads versioned feature snapshots."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.generator = FeatureGenerator()

    def generate_snapshots(self) -> int:
        dataset_version = self.current_dataset_version()
        customers = list(
            self.session.scalars(
                select(Customer)
                .options(
                    selectinload(Customer.loans),
                    selectinload(Customer.products),
                    selectinload(Customer.transactions),
                )
                .order_by(Customer.customer_id)
            )
        )
        generated_at = datetime.now(UTC)
        count = 0

        for customer in customers:
            feature_payload = {
                "values": self.generator.generate_for_customer(customer),
                "descriptions": self.generator.describe_features(),
            }
            existing = self.session.scalar(
                select(FeatureSnapshot).where(
                    FeatureSnapshot.customer_id == customer.customer_id,
                    FeatureSnapshot.feature_version == FEATURE_VERSION,
                    FeatureSnapshot.dataset_version == dataset_version,
                )
            )
            if existing is None:
                self.session.add(
                    FeatureSnapshot(
                        customer_id=customer.customer_id,
                        feature_version=FEATURE_VERSION,
                        dataset_version=dataset_version,
                        features=feature_payload,
                        generated_at=generated_at,
                    )
                )
            else:
                existing.features = feature_payload
                existing.generated_at = generated_at
            count += 1

        self.session.commit()
        return count

    def latest_for_customer(self, customer_id: str) -> FeatureSnapshot | None:
        return self.session.scalar(
            select(FeatureSnapshot)
            .where(FeatureSnapshot.customer_id == customer_id)
            .order_by(FeatureSnapshot.generated_at.desc())
            .limit(1)
        )

    def current_dataset_version(self) -> str:
        metadata = list(
            self.session.scalars(
                select(DatasetMetadata).order_by(DatasetMetadata.dataset_name)
            )
        )
        if not metadata:
            return "no_datasets"
        digest = hashlib.sha256()
        for item in metadata:
            digest.update(
                f"{item.dataset_name}|{item.version}|{item.checksum}".encode()
            )
        return digest.hexdigest()[:16]

    def status(self) -> dict[str, Any]:
        snapshot_count = (
            self.session.scalar(select(func.count(FeatureSnapshot.id))) or 0
        )
        customer_count = (
            self.session.scalar(select(func.count(Customer.customer_id))) or 0
        )
        latest = self.session.scalar(
            select(FeatureSnapshot)
            .order_by(FeatureSnapshot.generated_at.desc())
            .limit(1)
        )
        return {
            "feature_version": FEATURE_VERSION,
            "dataset_version": self.current_dataset_version(),
            "snapshot_count": snapshot_count,
            "customer_count": customer_count,
            "latest_generated_at": latest.generated_at if latest else None,
            "feature_count": len(FEATURE_DEFINITIONS),
            "coverage": (
                round(snapshot_count / customer_count, 4) if customer_count else 0.0
            ),
        }
