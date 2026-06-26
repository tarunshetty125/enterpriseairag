from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.datasets.types import QualityCheck, QualityReport
from app.models.canonical import Customer, DatasetMetadata, Loan


class DataQualityService:
    """Runs deterministic validation checks against canonical data."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def report(self) -> QualityReport:
        checks = [
            self._missing_dataset_metadata(),
            self._duplicate_customers(),
            self._missing_income(),
            self._negative_income(),
            self._invalid_credit_scores(),
            self._broken_loan_records(),
        ]
        failed_penalty = sum(
            check.affected_rows * 2.0 for check in checks if check.status == "failed"
        )
        warning_penalty = sum(
            check.affected_rows * 0.01 for check in checks if check.status == "warning"
        )
        score = max(0.0, round(100.0 - min(failed_penalty + warning_penalty, 100.0), 2))
        return QualityReport(score=score, checks=checks)

    def _missing_dataset_metadata(self) -> QualityCheck:
        count = (
            self.session.scalar(select(func.count(DatasetMetadata.dataset_name))) or 0
        )
        return QualityCheck(
            name="Dataset Metadata",
            status="passed" if count > 0 else "failed",
            affected_rows=0 if count > 0 else 1,
            details=f"{count} dataset metadata records available",
        )

    def _duplicate_customers(self) -> QualityCheck:
        duplicate_count = (
            self.session.execute(
                select(func.count())
                .select_from(Customer)
                .group_by(Customer.customer_id)
                .having(func.count(Customer.customer_id) > 1)
            )
            .scalars()
            .all()
        )
        affected = len(duplicate_count)
        return QualityCheck(
            name="Duplicate Customers",
            status="passed" if affected == 0 else "failed",
            affected_rows=affected,
            details="Customer primary keys are unique",
        )

    def _missing_income(self) -> QualityCheck:
        affected = (
            self.session.scalar(
                select(func.count(Customer.customer_id)).where(
                    Customer.estimated_income.is_(None)
                )
            )
            or 0
        )
        return QualityCheck(
            name="Missing Income",
            status="passed" if affected == 0 else "warning",
            affected_rows=affected,
            details="Customers without estimated income are allowed but flagged",
        )

    def _negative_income(self) -> QualityCheck:
        affected = (
            self.session.scalar(
                select(func.count(Customer.customer_id)).where(
                    Customer.estimated_income < 0
                )
            )
            or 0
        )
        return QualityCheck(
            name="Negative Income",
            status="passed" if affected == 0 else "failed",
            affected_rows=affected,
            details="Estimated income must not be negative",
        )

    def _invalid_credit_scores(self) -> QualityCheck:
        affected = (
            self.session.scalar(
                select(func.count(Customer.customer_id)).where(
                    Customer.credit_score.is_not(None),
                    (Customer.credit_score < 300) | (Customer.credit_score > 900),
                )
            )
            or 0
        )
        return QualityCheck(
            name="Invalid Credit Score",
            status="passed" if affected == 0 else "failed",
            affected_rows=affected,
            details="Credit scores must be between 300 and 900 when present",
        )

    def _broken_loan_records(self) -> QualityCheck:
        affected = (
            self.session.scalar(
                select(func.count(Loan.id)).where(
                    (Loan.amount < 0) | (Loan.customer_id.is_(None))
                )
            )
            or 0
        )
        return QualityCheck(
            name="Broken Loan Records",
            status="passed" if affected == 0 else "failed",
            affected_rows=affected,
            details="Loans must have a customer and non-negative amount",
        )
