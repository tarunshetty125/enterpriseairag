from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.serializers import (
    serialize_behaviour_profile,
    serialize_product,
    serialize_recommendation,
    serialize_recommendation_history,
    serialize_recommendation_rule,
    serialize_transaction_insight,
)
from app.datasets.service import DatasetService
from app.db.session import get_db_session
from app.nlp.services.intelligence import NLPIntelligenceService
from app.recommendation.service import RecommendationService
from app.schemas.intelligence import (
    BehaviourProfileResponse,
    IntelligenceStatusResponse,
    RecommendationGenerationResponse,
    RecommendationListResponse,
    RecommendationRuleResponse,
    TransactionInsightsResponse,
)

router = APIRouter(tags=["intelligence"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get(
    "/transactions/{customer_id}/insights",
    response_model=TransactionInsightsResponse,
)
def get_transaction_insights(
    customer_id: str,
    session: DbSession,
) -> TransactionInsightsResponse:
    try:
        results = NLPIntelligenceService(session).transaction_insights(customer_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    category_distribution: Counter[str] = Counter()
    spending_distribution: defaultdict[str, float] = defaultdict(float)
    insights = []
    for result in results:
        insight = result.insight
        transaction = result.transaction
        category_distribution[insight.category] += 1
        if transaction.direction == "debit":
            spending_distribution[insight.category] += transaction.amount
        insights.append(serialize_transaction_insight(insight, transaction))

    return TransactionInsightsResponse(
        customer_id=customer_id,
        total=len(insights),
        insights=insights,
        category_distribution=dict(sorted(category_distribution.items())),
        spending_distribution={
            category: round(amount, 2)
            for category, amount in sorted(spending_distribution.items())
        },
    )


@router.get(
    "/customers/{customer_id}/behaviour",
    response_model=BehaviourProfileResponse,
)
def get_customer_behaviour(
    customer_id: str,
    session: DbSession,
) -> BehaviourProfileResponse:
    try:
        profile = NLPIntelligenceService(session).behaviour_profile(customer_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return serialize_behaviour_profile(profile)


@router.post(
    "/recommendations/generate/{customer_id}",
    response_model=RecommendationGenerationResponse,
)
def generate_recommendations(
    customer_id: str,
    session: DbSession,
) -> RecommendationGenerationResponse:
    try:
        recommendations = RecommendationService(session).generate_for_customer(
            customer_id
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RecommendationGenerationResponse(
        customer_id=customer_id,
        generated=len(recommendations),
        recommendations=[
            serialize_recommendation(recommendation)
            for recommendation in recommendations
        ],
    )


@router.get(
    "/recommendations/{customer_id}",
    response_model=RecommendationListResponse,
)
def get_recommendations(
    customer_id: str,
    session: DbSession,
) -> RecommendationListResponse:
    service = RecommendationService(session)
    dataset_service = DatasetService(session)
    customer = dataset_service.get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return RecommendationListResponse(
        customer_id=customer_id,
        current_products=[
            serialize_product(product)
            for product in customer.products
            if product.status.lower() == "active"
        ],
        recommendations=[
            serialize_recommendation(recommendation)
            for recommendation in service.list_for_customer(customer_id)
        ],
        history=[
            serialize_recommendation_history(history)
            for history in service.history_for_customer(customer_id)
        ],
    )


@router.get(
    "/recommendation-rules",
    response_model=list[RecommendationRuleResponse],
)
def get_recommendation_rules(
    session: DbSession,
) -> list[RecommendationRuleResponse]:
    return [
        serialize_recommendation_rule(rule)
        for rule in RecommendationService(session).list_rules()
    ]


@router.get(
    "/intelligence/status",
    response_model=IntelligenceStatusResponse,
)
def get_intelligence_status(
    session: DbSession,
) -> IntelligenceStatusResponse:
    nlp_status = NLPIntelligenceService(session).status()
    recommendation_service = RecommendationService(session)
    recommendation_service.seed_rules()
    recommendation_status = recommendation_service.status()
    return IntelligenceStatusResponse(
        nlp_processing_version=str(nlp_status["nlp_processing_version"]),
        transactions_processed=_int_metric(nlp_status["transactions_processed"]),
        behaviour_profiles_generated=_int_metric(
            nlp_status["behaviour_profiles_generated"]
        ),
        average_nlp_processing_time_ms=_float_metric(
            nlp_status["average_nlp_processing_time_ms"]
        ),
        latest_behaviour_profile_at=_datetime_metric(
            nlp_status["latest_behaviour_profile_at"]
        ),
        recommendation_rule_version=str(
            recommendation_status["recommendation_rule_version"]
        ),
        recommendation_rule_count=_int_metric(
            recommendation_status["recommendation_rule_count"]
        ),
        recommendation_count=_int_metric(recommendation_status["recommendation_count"]),
        recommendation_history_count=_int_metric(
            recommendation_status["recommendation_history_count"]
        ),
        latest_recommendation_at=_datetime_metric(
            recommendation_status["latest_recommendation_at"]
        ),
    )


def _int_metric(value: object) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return 0


def _float_metric(value: object) -> float:
    if isinstance(value, int | float):
        return float(value)
    return 0.0


def _datetime_metric(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return value
    return None
