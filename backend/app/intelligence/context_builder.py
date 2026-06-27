from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from app.datasets.service import DatasetService
from app.ml.pipelines.prediction import PredictionPipeline
from app.nlp.services.intelligence import NLPIntelligenceService
from app.recommendation.service import RecommendationService


@dataclass(frozen=True)
class ContextChunk:
    document: str
    section: str
    chunk_id: int
    similarity_score: float
    content: str


@dataclass(frozen=True)
class StructuredContext:
    customer_profile: dict[str, Any] | None = None
    feature_store: dict[str, Any] | None = None
    risk_prediction: dict[str, Any] | None = None
    behaviour_profile: dict[str, Any] | None = None
    recommendations: list[dict[str, Any]] = field(default_factory=list)
    conversation_history: list[dict[str, Any]] = field(default_factory=list)
    retrieved_chunks: list[ContextChunk] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "customer_profile": self.customer_profile,
            "feature_store": self.feature_store,
            "risk_prediction": self.risk_prediction,
            "behaviour_profile": self.behaviour_profile,
            "recommendations": self.recommendations,
            "conversation_history": self.conversation_history,
            "retrieved_chunks": [
                {
                    "document": chunk.document,
                    "section": chunk.section,
                    "chunk_id": chunk.chunk_id,
                    "similarity_score": chunk.similarity_score,
                    "content": chunk.content,
                }
                for chunk in self.retrieved_chunks
            ],
        }


class ContextBuilder:
    """Builds structured context from source-of-truth services."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def build(
        self,
        *,
        customer_id: str | None = None,
        conversation_history: list[dict[str, Any]] | None = None,
        retrieved_chunks: list[ContextChunk] | None = None,
    ) -> StructuredContext:
        customer_profile = None
        feature_store = None
        risk_prediction = None
        behaviour_profile = None
        recommendations: list[dict[str, Any]] = []
        if customer_id:
            dataset_service = DatasetService(self.session)
            customer = dataset_service.get_customer(customer_id)
            if customer is not None:
                customer_profile = {
                    "customer_id": customer.customer_id,
                    "full_name": customer.full_name,
                    "age": customer.age,
                    "income_category": customer.income_category,
                    "estimated_income": customer.estimated_income,
                    "credit_score": customer.credit_score,
                }
                snapshot = dataset_service.latest_feature_snapshot(customer_id)
                feature_store = (
                    snapshot.features.get("values")
                    if snapshot is not None and isinstance(snapshot.features, dict)
                    else None
                )
                risk_prediction = self._risk_prediction(customer_id)
                behaviour_profile = self._behaviour_profile(customer_id)
                recommendations = self._recommendations(customer_id)
        return StructuredContext(
            customer_profile=customer_profile,
            feature_store=feature_store,
            risk_prediction=risk_prediction,
            behaviour_profile=behaviour_profile,
            recommendations=recommendations,
            conversation_history=conversation_history or [],
            retrieved_chunks=retrieved_chunks or [],
        )

    def _risk_prediction(self, customer_id: str) -> dict[str, Any] | None:
        try:
            prediction = PredictionPipeline(self.session).predict_risk(customer_id)
        except ValueError:
            return None
        return {
            "risk_level": prediction.risk_level,
            "confidence": prediction.confidence,
            "model_version": prediction.model_version,
            "top_features": [
                {
                    "name": feature.name,
                    "value": feature.value,
                    "importance": feature.importance,
                }
                for feature in prediction.top_features
            ],
        }

    def _behaviour_profile(self, customer_id: str) -> dict[str, Any] | None:
        try:
            profile = NLPIntelligenceService(self.session).behaviour_profile(
                customer_id
            )
        except ValueError:
            return None
        return {
            "summary": profile.summary,
            "flags": profile.flags,
            "lifestyle_indicators": profile.lifestyle_indicators,
            "category_spend": profile.category_spend,
        }

    def _recommendations(self, customer_id: str) -> list[dict[str, Any]]:
        try:
            rows = RecommendationService(self.session).list_for_customer(customer_id)
        except ValueError:
            return []
        return [
            {
                "product_name": row.product_name,
                "suitability_score": row.suitability_score,
                "reason": row.reason,
                "supporting_features": row.supporting_features,
            }
            for row in rows
        ]
