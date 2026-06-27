from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.customers import ProductResponse
from app.schemas.settings import to_camel


class TransactionInsightResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    transaction_id: int
    customer_id: str
    amount: float
    direction: str
    transaction_type: str
    raw_description: str
    category: str
    keywords: list[str]
    entities: dict[str, Any]
    sentiment_label: str
    sentiment_score: float
    lifestyle_indicators: list[str]
    processed_at: datetime


class TransactionInsightsResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    customer_id: str
    total: int
    insights: list[TransactionInsightResponse]
    category_distribution: dict[str, int]
    spending_distribution: dict[str, float]


class BehaviourProfileResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    customer_id: str
    profile_version: str
    summary: str
    flags: list[str]
    lifestyle_indicators: list[str]
    category_spend: dict[str, float]
    category_counts: dict[str, int]
    monthly_trends: list[dict[str, Any]]
    top_merchants: list[dict[str, Any]]
    features: dict[str, Any]
    processing_time_ms: float
    generated_at: datetime


class RecommendationRuleResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    rule_id: str
    product_name: str
    description: str
    conditions: dict[str, Any]
    base_score: float
    version: str
    active: bool


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    customer_id: str
    rule_id: str
    product_name: str
    suitability_score: float
    confidence: float
    reason: str
    supporting_features: list[dict[str, Any]]
    business_explanation: str
    recommendation_version: str
    status: str
    generated_at: datetime


class RecommendationHistoryResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    customer_id: str
    recommendation_id: int | None
    action: str
    details: dict[str, Any]
    created_at: datetime


class RecommendationListResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    customer_id: str
    current_products: list[ProductResponse]
    recommendations: list[RecommendationResponse]
    history: list[RecommendationHistoryResponse]


class RecommendationGenerationResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    customer_id: str
    generated: int
    recommendations: list[RecommendationResponse]


class IntelligenceStatusResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    nlp_processing_version: str
    transactions_processed: int
    behaviour_profiles_generated: int
    average_nlp_processing_time_ms: float
    latest_behaviour_profile_at: datetime | None
    recommendation_rule_version: str
    recommendation_rule_count: int
    recommendation_count: int
    recommendation_history_count: int
    latest_recommendation_at: datetime | None
