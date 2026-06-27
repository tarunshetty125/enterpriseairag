from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from time import perf_counter
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, selectinload

from app.feature_store.service import FeatureStoreService
from app.ml.pipelines.prediction import PredictionPipeline
from app.models.canonical import Customer
from app.models.intelligence import (
    BehaviourProfile,
    Recommendation,
    RecommendationHistory,
    RecommendationRule,
)
from app.nlp.services.intelligence import NLPIntelligenceService
from app.recommendation.rules import (
    PRODUCT_RULES,
    RECOMMENDATION_RULE_VERSION,
    ProductRule,
)


@dataclass(frozen=True)
class RecommendationContext:
    customer: Customer
    features: dict[str, Any]
    behaviour: BehaviourProfile
    risk_level: str
    segment_label: str
    current_products: list[str]


@dataclass(frozen=True)
class ScoredRecommendation:
    rule_id: str
    product_name: str
    suitability_score: float
    confidence: float
    reason: str
    supporting_features: list[dict[str, Any]]
    business_explanation: str


class RecommendationService:
    """Generates deterministic, explainable financial product recommendations."""

    def __init__(self, session: Session, use_model_predictions: bool = True) -> None:
        self.session = session
        self.use_model_predictions = use_model_predictions
        self.features = FeatureStoreService(session)

    def seed_rules(self) -> int:
        """Upsert the deterministic recommendation rule catalog."""

        count = 0
        for rule in PRODUCT_RULES:
            existing = self.session.scalar(
                select(RecommendationRule).where(
                    RecommendationRule.rule_id == rule.rule_id
                )
            )
            payload = {
                "product_name": rule.product_name,
                "description": rule.description,
                "conditions": rule.conditions,
                "base_score": rule.base_score,
                "version": RECOMMENDATION_RULE_VERSION,
                "active": 1,
            }
            if existing is None:
                self.session.add(RecommendationRule(rule_id=rule.rule_id, **payload))
            else:
                for key, value in payload.items():
                    setattr(existing, key, value)
            count += 1
        self.session.commit()
        return count

    def list_rules(self) -> list[RecommendationRule]:
        self.seed_rules()
        return list(
            self.session.scalars(
                select(RecommendationRule)
                .where(RecommendationRule.active == 1)
                .order_by(RecommendationRule.product_name)
            )
        )

    def generate_for_customer(
        self,
        customer_id: str,
        *,
        refresh_intelligence: bool = True,
        ensure_rules: bool = True,
    ) -> list[Recommendation]:
        if ensure_rules:
            self.seed_rules()
        context = self._context(
            customer_id,
            refresh_intelligence=refresh_intelligence,
        )
        started = perf_counter()
        scored = [
            recommendation
            for recommendation in (
                self._score_rule(rule, context) for rule in PRODUCT_RULES
            )
            if recommendation.suitability_score >= 45.0
        ]
        scored.sort(key=lambda item: item.suitability_score, reverse=True)
        selected = scored[:6]

        self.session.execute(
            update(Recommendation)
            .where(
                Recommendation.customer_id == customer_id,
                Recommendation.status == "active",
            )
            .values(status="superseded")
        )

        generated_at = datetime.now(UTC)
        recommendations: list[Recommendation] = []
        for item in selected:
            recommendation = Recommendation(
                customer_id=customer_id,
                rule_id=item.rule_id,
                product_name=item.product_name,
                suitability_score=item.suitability_score,
                confidence=item.confidence,
                reason=item.reason,
                supporting_features=item.supporting_features,
                business_explanation=item.business_explanation,
                recommendation_version=RECOMMENDATION_RULE_VERSION,
                status="active",
                generated_at=generated_at,
            )
            self.session.add(recommendation)
            self.session.flush()
            self.session.add(
                RecommendationHistory(
                    customer_id=customer_id,
                    recommendation_id=recommendation.id,
                    action="generated",
                    details={
                        "product_name": recommendation.product_name,
                        "suitability_score": recommendation.suitability_score,
                        "risk_level": context.risk_level,
                        "segment_label": context.segment_label,
                        "processing_time_ms": round(
                            (perf_counter() - started) * 1000,
                            3,
                        ),
                    },
                )
            )
            recommendations.append(recommendation)

        if not selected:
            self.session.add(
                RecommendationHistory(
                    customer_id=customer_id,
                    recommendation_id=None,
                    action="no_recommendation",
                    details={
                        "risk_level": context.risk_level,
                        "segment_label": context.segment_label,
                        "reason": (
                            "No product rule reached the minimum suitability "
                            "threshold."
                        ),
                    },
                )
            )
        self.session.commit()
        for recommendation in recommendations:
            self.session.refresh(recommendation)
        return recommendations

    def list_for_customer(self, customer_id: str) -> list[Recommendation]:
        self._customer(customer_id)
        return list(
            self.session.scalars(
                select(Recommendation)
                .where(
                    Recommendation.customer_id == customer_id,
                    Recommendation.status == "active",
                )
                .order_by(
                    Recommendation.suitability_score.desc(),
                    Recommendation.generated_at.desc(),
                )
            )
        )

    def history_for_customer(self, customer_id: str) -> list[RecommendationHistory]:
        self._customer(customer_id)
        return list(
            self.session.scalars(
                select(RecommendationHistory)
                .where(RecommendationHistory.customer_id == customer_id)
                .order_by(RecommendationHistory.created_at.desc())
                .limit(25)
            )
        )

    def current_products(self, customer_id: str) -> list[str]:
        customer = self._customer(customer_id)
        products = sorted(
            {
                product.product_type
                for product in customer.products
                if product.status.lower() == "active"
            }
        )
        return products

    def status(self) -> dict[str, int | str | float | datetime | None]:
        latest_recommendation = self.session.scalar(
            select(Recommendation).order_by(Recommendation.generated_at.desc()).limit(1)
        )
        return {
            "recommendation_rule_version": RECOMMENDATION_RULE_VERSION,
            "recommendation_rule_count": self.session.scalar(
                select(func.count(RecommendationRule.id)).where(
                    RecommendationRule.active == 1
                )
            )
            or 0,
            "recommendation_count": self.session.scalar(
                select(func.count(Recommendation.id)).where(
                    Recommendation.status == "active"
                )
            )
            or 0,
            "recommendation_history_count": self.session.scalar(
                select(func.count(RecommendationHistory.id))
            )
            or 0,
            "latest_recommendation_at": (
                latest_recommendation.generated_at
                if latest_recommendation is not None
                else None
            ),
        }

    def _context(
        self,
        customer_id: str,
        *,
        refresh_intelligence: bool,
    ) -> RecommendationContext:
        customer = self._customer(customer_id)
        behaviour_service = NLPIntelligenceService(self.session)
        if refresh_intelligence:
            behaviour = behaviour_service.behaviour_profile(customer_id)
        else:
            existing_behaviour = behaviour_service.behaviour.get_profile(customer_id)
            if existing_behaviour is None:
                behaviour = behaviour_service.behaviour_profile(customer_id)
            else:
                behaviour = existing_behaviour
        feature_values = self._feature_values(customer_id)
        risk_level = self._risk_level(customer_id, customer, feature_values)
        segment_label = self._segment_label(
            customer_id, customer, feature_values, behaviour
        )
        return RecommendationContext(
            customer=customer,
            features=feature_values,
            behaviour=behaviour,
            risk_level=risk_level,
            segment_label=segment_label,
            current_products=self.current_products(customer_id),
        )

    def _customer(self, customer_id: str) -> Customer:
        customer = self.session.scalar(
            select(Customer)
            .where(Customer.customer_id == customer_id)
            .options(selectinload(Customer.products), selectinload(Customer.loans))
        )
        if customer is None:
            msg = f"Customer not found: {customer_id}"
            raise ValueError(msg)
        return customer

    def _feature_values(self, customer_id: str) -> dict[str, Any]:
        snapshot = self.features.latest_for_customer(customer_id)
        if snapshot is None or not isinstance(snapshot.features, dict):
            return {}
        values = snapshot.features.get("values", {})
        return values if isinstance(values, dict) else {}

    def _risk_level(
        self,
        customer_id: str,
        customer: Customer,
        features: dict[str, Any],
    ) -> str:
        if not self.use_model_predictions:
            return self._feature_risk_level(customer, features)
        try:
            return PredictionPipeline(self.session).predict_risk(customer_id).risk_level
        except ValueError:
            return self._feature_risk_level(customer, features)

    def _segment_label(
        self,
        customer_id: str,
        customer: Customer,
        features: dict[str, Any],
        behaviour: BehaviourProfile,
    ) -> str:
        if not self.use_model_predictions:
            return self._feature_segment_label(customer, features, behaviour)
        try:
            return (
                PredictionPipeline(self.session)
                .predict_segment(customer_id)
                .segment_label
            )
        except ValueError:
            return self._feature_segment_label(customer, features, behaviour)

    def _feature_risk_level(
        self,
        customer: Customer,
        features: dict[str, Any],
    ) -> str:
        debt_to_income = self._float(features.get("debt_to_income"))
        credit_score = float(customer.credit_score) if customer.credit_score else 700.0
        risk_indicators = self._float(features.get("risk_indicators"))
        if debt_to_income >= 1.5 or risk_indicators >= 2 or credit_score < 600:
            return "High"
        if debt_to_income >= 0.5 or risk_indicators >= 1 or credit_score < 700:
            return "Medium"
        return "Low"

    def _feature_segment_label(
        self,
        customer: Customer,
        features: dict[str, Any],
        behaviour: BehaviourProfile,
    ) -> str:
        flags = set(behaviour.flags)
        income = customer.estimated_income or 0.0
        age = customer.age or 0
        savings_ratio = self._float(features.get("savings_ratio"))
        debt_to_income = self._float(features.get("debt_to_income"))
        if debt_to_income >= 1.5 or "High EMI Burden" in flags:
            return "Loan Focused"
        if income >= 120000 or savings_ratio >= 1.0:
            return "Premium"
        if income >= 80000:
            return "High Value"
        if age and age < 35:
            return "Young Investors"
        return "Budget"

    def _score_rule(
        self,
        rule: ProductRule,
        context: RecommendationContext,
    ) -> ScoredRecommendation:
        conditions = rule.conditions
        score = float(rule.base_score)
        supporting_features: list[dict[str, Any]] = []
        flags = set(context.behaviour.flags)
        existing_products = {name.lower() for name in context.current_products}

        if context.risk_level in conditions.get("risk_levels", []):
            score += 12.0
            supporting_features.append(
                self._support("Risk Level", context.risk_level, 12.0)
            )
        elif "risk_levels" in conditions:
            score -= 18.0
            supporting_features.append(
                self._support("Risk Level", context.risk_level, -18.0)
            )

        min_income = conditions.get("min_income")
        if min_income is not None:
            income = context.customer.estimated_income or 0.0
            impact = 12.0 if income >= float(min_income) else -10.0
            score += impact
            supporting_features.append(
                self._support("Estimated Income", income, impact)
            )

        min_age = conditions.get("min_age")
        if min_age is not None:
            age = context.customer.age or 0
            impact = 9.0 if age >= int(min_age) else -6.0
            score += impact
            supporting_features.append(self._support("Age", age, impact))

        max_dti = conditions.get("max_debt_to_income")
        if max_dti is not None:
            debt_to_income = self._float(context.features.get("debt_to_income"))
            impact = 12.0 if debt_to_income <= float(max_dti) else -18.0
            score += impact
            supporting_features.append(
                self._support("Debt To Income", debt_to_income, impact)
            )

        min_savings_ratio = conditions.get("min_savings_ratio")
        if min_savings_ratio is not None:
            savings_ratio = self._float(context.features.get("savings_ratio"))
            impact = 12.0 if savings_ratio >= float(min_savings_ratio) else -8.0
            score += impact
            supporting_features.append(
                self._support("Savings Ratio", savings_ratio, impact)
            )

        min_savings_balance = conditions.get("min_savings_balance")
        if min_savings_balance is not None:
            savings = context.customer.savings_balance or 0.0
            impact = 10.0 if savings >= float(min_savings_balance) else -8.0
            score += impact
            supporting_features.append(
                self._support("Savings Balance", savings, impact)
            )

        for required_flag in conditions.get("required_flags", []):
            impact = 14.0 if required_flag in flags else -14.0
            score += impact
            supporting_features.append(
                self._support(
                    f"Behaviour Flag: {required_flag}", required_flag in flags, impact
                )
            )

        for positive_flag in conditions.get("positive_flags", []):
            if positive_flag in flags:
                score += 9.0
                supporting_features.append(
                    self._support(f"Behaviour Flag: {positive_flag}", True, 9.0)
                )

        if rule.product_name.lower() in existing_products:
            score -= 20.0
            supporting_features.append(
                self._support("Existing Product", rule.product_name, -20.0)
            )

        segment_impact = self._segment_bonus(rule.product_name, context)
        if segment_impact != 0.0:
            score += segment_impact
            supporting_features.append(
                self._support("Customer Segment", context.segment_label, segment_impact)
            )

        score = max(0.0, min(100.0, round(score, 2)))
        confidence = round(score / 100, 4)
        reason = self._reason(rule.product_name, supporting_features)
        return ScoredRecommendation(
            rule_id=str(rule.rule_id),
            product_name=str(rule.product_name),
            suitability_score=score,
            confidence=confidence,
            reason=reason,
            supporting_features=supporting_features,
            business_explanation=(
                f"Recommended {rule.product_name} because the customer is "
                f"{context.risk_level.lower()} risk, belongs to the "
                f"{context.segment_label} segment, and the supporting factors "
                "match the active rule set."
            ),
        )

    def _segment_bonus(
        self,
        product_name: str,
        context: RecommendationContext,
    ) -> float:
        flags = set(context.behaviour.flags)
        if product_name == "Credit Card" and (
            "Frequent Traveller" in flags or "High Online Shopper" in flags
        ):
            return 8.0
        if product_name == "Home Loan" and context.segment_label in {
            "Premium",
            "High Value",
            "Loan Focused",
        }:
            return 6.0
        if product_name in {"Mutual Fund", "SIP"} and context.segment_label in {
            "Premium",
            "High Value",
            "Young Investors",
        }:
            return 7.0
        if product_name == "Fixed Deposit" and context.segment_label in {
            "Premium",
            "High Value",
        }:
            return 6.0
        return 0.0

    def _reason(
        self,
        product_name: str,
        supporting_features: list[dict[str, Any]],
    ) -> str:
        positive = [
            str(feature["name"])
            for feature in supporting_features
            if self._float(feature.get("impact")) > 0
        ][:3]
        if positive:
            return f"{product_name} fits because of {', '.join(positive)}."
        return f"{product_name} is the best available match from the active rules."

    def _support(self, name: str, value: Any, impact: float) -> dict[str, Any]:
        return {
            "name": name,
            "value": value,
            "impact": round(impact, 2),
        }

    def _float(self, value: Any) -> float:
        if isinstance(value, int | float):
            return float(value)
        return 0.0
