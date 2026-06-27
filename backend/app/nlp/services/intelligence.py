from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.canonical import Customer, Transaction
from app.models.intelligence import BehaviourProfile, TransactionInsight
from app.nlp.behaviour.profile import BehaviourProfileService
from app.nlp.pipelines.transaction_intelligence import (
    NLP_PROCESSING_VERSION,
    TransactionInsightResult,
    TransactionIntelligencePipeline,
)


class NLPIntelligenceService:
    """Coordinates transaction NLP and customer behaviour profile generation."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.pipeline = TransactionIntelligencePipeline(session)
        self.behaviour = BehaviourProfileService(session)

    def transaction_insights(self, customer_id: str) -> list[TransactionInsightResult]:
        self._ensure_customer(customer_id)
        return self.pipeline.process_customer(customer_id)

    def behaviour_profile(self, customer_id: str) -> BehaviourProfile:
        self._ensure_customer(customer_id)
        self.pipeline.process_customer(customer_id)
        return self.behaviour.generate_profile(customer_id)

    def process_all(self) -> dict[str, int | float | str | datetime | None]:
        transaction_count = self.pipeline.process_all()
        customer_ids = list(
            self.session.scalars(
                select(Transaction.customer_id)
                .distinct()
                .order_by(Transaction.customer_id)
            )
        )
        for customer_id in customer_ids:
            self.behaviour.generate_profile(customer_id)
        return self.status() | {"processed_transactions": transaction_count}

    def status(self) -> dict[str, int | float | str | datetime | None]:
        latest_profile = self.session.scalar(
            select(BehaviourProfile)
            .order_by(BehaviourProfile.generated_at.desc())
            .limit(1)
        )
        average_processing_time = self.session.scalar(
            select(func.avg(TransactionInsight.processing_time_ms))
        )
        return {
            "nlp_processing_version": NLP_PROCESSING_VERSION,
            "transactions_processed": self.session.scalar(
                select(func.count(TransactionInsight.id))
            )
            or 0,
            "behaviour_profiles_generated": self.session.scalar(
                select(func.count(BehaviourProfile.customer_id))
            )
            or 0,
            "average_nlp_processing_time_ms": round(
                float(average_processing_time or 0.0), 3
            ),
            "latest_behaviour_profile_at": (
                latest_profile.generated_at if latest_profile else None
            ),
        }

    def _ensure_customer(self, customer_id: str) -> None:
        exists = self.session.scalar(
            select(Customer.customer_id).where(Customer.customer_id == customer_id)
        )
        if exists is None:
            msg = f"Customer not found: {customer_id}"
            raise ValueError(msg)
