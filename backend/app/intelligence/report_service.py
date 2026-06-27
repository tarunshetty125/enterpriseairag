from __future__ import annotations

import hashlib
import json
import textwrap
from collections.abc import Callable
from dataclasses import dataclass
from time import perf_counter
from typing import Any, TypeVar

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.datasets.service import DatasetService
from app.gateway.ai_gateway import AIGateway, GatewayRequest
from app.ml.pipelines.prediction import (
    PredictionPipeline,
    RiskPredictionResult,
    SegmentPredictionResult,
)
from app.models.ai import AIMetricLog, KnowledgeDocument
from app.models.canonical import Customer, FeatureSnapshot, utc_now
from app.models.intelligence import (
    BehaviourProfile,
    CustomerIntelligenceReport,
    Recommendation,
)
from app.models.ml import MLModelRegistry
from app.nlp.services.intelligence import NLPIntelligenceService
from app.prompts.manager import PromptManager
from app.providers.base import ProviderConfigurationError, ProviderMessage, TokenUsage
from app.providers.manager import ProviderManager
from app.rag.service import Citation, RAGService, RetrievalResult
from app.recommendation.service import RecommendationService

REPORT_VERSION = "v1"
T = TypeVar("T")


@dataclass(frozen=True)
class ExportedReport:
    content: bytes
    media_type: str
    filename: str


class CustomerIntelligenceService:
    """Final service composing data, ML, NLP, recommendations, RAG, and LLMs."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def generate_report(
        self,
        customer_id: str,
        *,
        force_regenerate: bool = False,
    ) -> dict[str, Any]:
        started = perf_counter()
        trace: list[dict[str, Any]] = []
        provider_settings = ProviderManager(self.session).current_settings()
        customer = self._stage(
            trace,
            "Customer Profile",
            "customers",
            lambda: self._customer(customer_id),
        )
        snapshot = self._stage(
            trace,
            "Feature Store",
            "feature_snapshots",
            lambda: DatasetService(self.session).latest_feature_snapshot(customer_id),
        )
        risk = self._stage(
            trace,
            "Risk Model",
            "ml_prediction",
            lambda: self._risk_prediction(customer_id),
        )
        segment = self._stage(
            trace,
            "Segmentation",
            "ml_prediction",
            lambda: self._segment_prediction(customer_id),
        )
        behaviour = self._stage(
            trace,
            "Behaviour Engine",
            "behaviour_profiles",
            lambda: self._behaviour_profile(customer_id),
        )
        insights = self._stage(
            trace,
            "Transaction Intelligence",
            "transaction_insights",
            lambda: NLPIntelligenceService(self.session).transaction_insights(
                customer_id
            ),
        )
        recommendations = self._stage(
            trace,
            "Recommendation Engine",
            "recommendations",
            lambda: self._recommendations(customer_id),
        )
        retrieved = self._stage(
            trace,
            "RAG",
            "knowledge_chunks",
            lambda: self._policy_evidence(customer, risk, segment, recommendations),
        )
        citations = [self._citation(item) for item in retrieved]
        evidence = self._evidence_payload(
            customer=customer,
            snapshot=snapshot,
            risk=risk,
            segment=segment,
            behaviour=behaviour,
            insights_count=len(insights),
            recommendations=recommendations,
            retrieved=retrieved,
            citations=citations,
        )
        input_hash = self._input_hash(
            customer=customer,
            snapshot=snapshot,
            risk=risk,
            segment=segment,
            behaviour=behaviour,
            recommendations=recommendations,
            citations=citations,
            provider=provider_settings.provider,
            model=provider_settings.model,
        )
        cached = self._cached(customer_id, input_hash)
        if cached is not None and not force_regenerate:
            cached.cache_hits += 1
            cached.updated_at = utc_now()
            self.session.commit()
            response = self._row_response(cached, cache_hit=True)
            response["workflow_trace"] = self._cache_trace(
                cached.workflow_trace,
                started,
            )
            return response

        context = self._context_payload(evidence)
        ai_summary, usage, latency_ms, prompt_version, status = self._stage(
            trace,
            "Provider",
            "ai_gateway",
            lambda: self._ai_summary(context, citations),
        )
        report = self._structured_report(
            evidence=evidence,
            ai_summary=ai_summary,
            status=status,
            provider=provider_settings.provider,
            model=provider_settings.model,
            prompt_version=prompt_version,
        )
        trace.append(
            {
                "stage": "Customer Intelligence Report",
                "source": "customer_intelligence_reports",
                "status": "success",
                "duration_ms": round((perf_counter() - started) * 1000, 2),
                "details": "Structured final report assembled",
            }
        )
        row = CustomerIntelligenceReport(
            customer_id=customer_id,
            report_version=REPORT_VERSION,
            input_hash=input_hash,
            status=status,
            report=report,
            evidence=evidence,
            workflow_trace=trace,
            provider=provider_settings.provider,
            model=provider_settings.model,
            prompt_version=prompt_version,
            latency_ms=latency_ms,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            retrieved_chunks=len(retrieved),
            context_size=len(json.dumps(context, default=str)),
            cache_hits=0,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return self._row_response(row, cache_hit=False)

    def latest_report(self, customer_id: str) -> dict[str, Any] | None:
        row = self._latest(customer_id)
        if row is None:
            return None
        return self._row_response(row, cache_hit=False)

    def workflow_trace(self, customer_id: str) -> list[dict[str, Any]]:
        row = self._latest(customer_id)
        return list(row.workflow_trace if row else [])

    def recent_reports(self, limit: int = 8) -> list[dict[str, Any]]:
        rows = self.session.scalars(
            select(CustomerIntelligenceReport)
            .order_by(CustomerIntelligenceReport.generated_at.desc())
            .limit(limit)
        )
        return [self._row_response(row, cache_hit=False) for row in rows]

    def showcase_metrics(self) -> dict[str, Any]:
        customers = self.session.scalar(select(func.count(Customer.customer_id))) or 0
        high_risk = self._risk_count("High")
        medium_risk = self._risk_count("Medium")
        low_risk = self._risk_count("Low")
        ai_metrics = self.session.scalar(select(func.count(AIMetricLog.id))) or 0
        latest_metric = self.session.scalar(
            select(AIMetricLog).order_by(AIMetricLog.created_at.desc()).limit(1)
        )
        provider_settings = ProviderManager(self.session).current_settings()
        risk_distribution = [
            {"label": "High", "value": high_risk},
            {"label": "Medium", "value": medium_risk},
            {"label": "Low", "value": low_risk},
        ]
        return {
            "customers": customers,
            "high_risk": high_risk,
            "medium_risk": medium_risk,
            "low_risk": low_risk,
            "segments": self._segment_counts(),
            "recommendations": self.session.scalar(
                select(func.count(Recommendation.id))
            )
            or 0,
            "knowledge_base": self.session.scalar(
                select(func.count(KnowledgeDocument.id))
            )
            or 0,
            "ai_requests": ai_metrics,
            "provider": provider_settings.provider,
            "current_model": provider_settings.model,
            "health": ProviderManager(self.session).active_provider().health().status,
            "recent_reports": self.recent_reports(limit=5),
            "risk_distribution": risk_distribution,
            "provider_usage": self._provider_usage(),
            "inference_latency_ms": (
                round(float(latest_metric.latency_ms), 2) if latest_metric else 0.0
            ),
            "report_count": self.session.scalar(
                select(func.count(CustomerIntelligenceReport.id))
            )
            or 0,
            "cache_hits": self.session.scalar(
                select(func.sum(CustomerIntelligenceReport.cache_hits))
            )
            or 0,
        }

    def export_report(
        self,
        customer_id: str,
        export_format: str,
    ) -> ExportedReport:
        row = self._latest(customer_id)
        if row is None:
            msg = f"No intelligence report found for {customer_id}."
            raise ValueError(msg)
        if export_format == "json":
            content = json.dumps(
                self._row_response(row, cache_hit=False),
                indent=2,
                default=str,
            )
            return ExportedReport(
                content=content.encode("utf-8"),
                media_type="application/json",
                filename=f"{customer_id}-intelligence-report.json",
            )
        markdown = self._markdown(row)
        if export_format == "markdown":
            return ExportedReport(
                content=markdown.encode("utf-8"),
                media_type="text/markdown",
                filename=f"{customer_id}-intelligence-report.md",
            )
        if export_format == "pdf":
            return ExportedReport(
                content=self._pdf(markdown),
                media_type="application/pdf",
                filename=f"{customer_id}-intelligence-report.pdf",
            )
        msg = "Unsupported export format. Use pdf, markdown, or json."
        raise ValueError(msg)

    def _stage(
        self,
        trace: list[dict[str, Any]],
        stage: str,
        source: str,
        operation: Callable[[], T],
    ) -> T:
        started = perf_counter()
        try:
            result = operation()
            trace.append(
                {
                    "stage": stage,
                    "source": source,
                    "status": "success",
                    "duration_ms": round((perf_counter() - started) * 1000, 2),
                    "details": self._stage_details(result),
                }
            )
            return result
        except ValueError as exc:
            trace.append(
                {
                    "stage": stage,
                    "source": source,
                    "status": "unavailable",
                    "duration_ms": round((perf_counter() - started) * 1000, 2),
                    "details": str(exc),
                }
            )
            raise

    def _customer(self, customer_id: str) -> Customer:
        customer = self.session.scalar(
            select(Customer)
            .where(Customer.customer_id == customer_id)
            .options(
                selectinload(Customer.loans),
                selectinload(Customer.products),
                selectinload(Customer.transactions),
            )
        )
        if customer is None:
            msg = f"Customer not found: {customer_id}"
            raise ValueError(msg)
        return customer

    def _risk_prediction(self, customer_id: str) -> RiskPredictionResult | None:
        try:
            return PredictionPipeline(self.session).predict_risk(customer_id)
        except ValueError:
            return None

    def _segment_prediction(self, customer_id: str) -> SegmentPredictionResult | None:
        try:
            return PredictionPipeline(self.session).predict_segment(customer_id)
        except ValueError:
            return None

    def _behaviour_profile(self, customer_id: str) -> BehaviourProfile | None:
        try:
            return NLPIntelligenceService(self.session).behaviour_profile(customer_id)
        except ValueError:
            return None

    def _recommendations(self, customer_id: str) -> list[Recommendation]:
        service = RecommendationService(self.session)
        service.seed_rules()
        rows = service.list_for_customer(customer_id)
        if rows:
            return rows
        try:
            return service.generate_for_customer(customer_id)
        except ValueError:
            return []

    def _policy_evidence(
        self,
        customer: Customer,
        risk: RiskPredictionResult | None,
        segment: SegmentPredictionResult | None,
        recommendations: list[Recommendation],
    ) -> list[RetrievalResult]:
        rag = RAGService(self.session)
        if int(rag.status()["chunk_count"]) == 0:
            rag.ingest()
        product_text = ", ".join(item.product_name for item in recommendations[:4])
        question = (
            "Retrieve banking policy evidence for customer eligibility, risk, "
            f"investment suitability, insurance, credit cards, and loans. "
            f"Customer credit score {customer.credit_score}; "
            f"risk {risk.risk_level if risk else 'unavailable'}; "
            f"segment {segment.segment_label if segment else 'unavailable'}; "
            f"recommended products {product_text or 'none'}."
        )
        return rag.retrieve(question)

    def _ai_summary(
        self,
        context: dict[str, Any],
        citations: list[Citation],
    ) -> tuple[str, TokenUsage, float, str, str]:
        prompt, template = PromptManager().render(
            "customer_intelligence_report",
            {
                "context": json.dumps(context, indent=2, default=str),
                "citations": self._citation_text(citations),
            },
        )
        settings = ProviderManager(self.session).current_settings()
        try:
            response = AIGateway(self.session).chat(
                GatewayRequest(
                    messages=[
                        ProviderMessage(role="system", content=prompt),
                        ProviderMessage(
                            role="user",
                            content=(
                                "Generate the grounded customer intelligence report."
                            ),
                        ),
                    ],
                    operation="customer_intelligence_report",
                    metadata={
                        "prompt": template.name,
                        "prompt_version": template.version,
                    },
                    retrieved_chunks=len(citations),
                    context_size=len(json.dumps(context, default=str)),
                )
            )
            return (
                response.content,
                response.usage,
                response.latency_ms,
                template.version,
                "success",
            )
        except ProviderConfigurationError:
            return (
                self._deterministic_summary(context, settings.provider, settings.model),
                TokenUsage(),
                0.0,
                template.version,
                "provider_not_configured",
            )
        except Exception as exc:
            return (
                f"AI provider fallback used because the provider call failed: {exc}",
                TokenUsage(),
                0.0,
                template.version,
                "provider_error_fallback",
            )

    def _evidence_payload(
        self,
        *,
        customer: Customer,
        snapshot: FeatureSnapshot | None,
        risk: RiskPredictionResult | None,
        segment: SegmentPredictionResult | None,
        behaviour: BehaviourProfile | None,
        insights_count: int,
        recommendations: list[Recommendation],
        retrieved: list[RetrievalResult],
        citations: list[Citation],
    ) -> dict[str, Any]:
        feature_values = self._feature_values(snapshot)
        return {
            "customer": {
                "customer_id": customer.customer_id,
                "full_name": customer.full_name,
                "age": customer.age,
                "income_category": customer.income_category,
                "estimated_income": customer.estimated_income,
                "credit_score": customer.credit_score,
                "savings_balance": customer.savings_balance,
                "tenure_months": customer.tenure_months,
                "products": [product.product_type for product in customer.products],
                "loans": [
                    {
                        "loan_type": loan.loan_type,
                        "amount": loan.amount,
                        "status": loan.status,
                    }
                    for loan in customer.loans
                ],
            },
            "feature_store": {
                "feature_version": snapshot.feature_version if snapshot else None,
                "dataset_version": snapshot.dataset_version if snapshot else None,
                "generated_at": snapshot.generated_at.isoformat() if snapshot else None,
                "values": feature_values,
            },
            "risk": self._risk_payload(risk),
            "segment": self._segment_payload(segment),
            "behaviour": self._behaviour_payload(behaviour, insights_count),
            "recommendations": [
                self._recommendation_payload(row) for row in recommendations
            ],
            "policy_evidence": {
                "retrieved_chunks": len(retrieved),
                "citations": [citation.__dict__ for citation in citations],
                "chunks": [
                    {
                        "document": item.chunk.document_name,
                        "section": item.chunk.section,
                        "chunk": item.chunk.id,
                        "similarity_score": item.score,
                        "content": item.chunk.content,
                    }
                    for item in retrieved
                ],
            },
        }

    def _structured_report(
        self,
        *,
        evidence: dict[str, Any],
        ai_summary: str,
        status: str,
        provider: str,
        model: str,
        prompt_version: str,
    ) -> dict[str, Any]:
        customer = self._dict_value(evidence.get("customer"))
        risk = self._dict_value(evidence.get("risk"))
        behaviour = self._dict_value(evidence.get("behaviour"))
        recommendations = self._list_value(evidence.get("recommendations"))
        policy = self._dict_value(evidence.get("policy_evidence"))
        risk_level = str(risk.get("risk_level") or "Unavailable")
        confidence = self._float(risk.get("confidence"))
        return {
            "title": "Customer Intelligence Report",
            "report_version": REPORT_VERSION,
            "executive_summary": {
                "customer": customer,
                "overall_assessment": (
                    f"{customer.get('full_name') or customer.get('customer_id')} is "
                    f"classified as {risk_level} risk with "
                    f"{round(confidence * 100, 1)}% model confidence."
                ),
                "evidence": [
                    "Canonical customer profile",
                    "Feature store snapshot",
                    "ML predictions",
                    "Behaviour profile",
                    "Recommendation engine",
                    "RAG policy citations",
                ],
                "confidence": self._section_confidence([confidence, 0.9, 0.85]),
            },
            "risk_assessment": {
                "current_risk": risk_level,
                "confidence": confidence,
                "probabilities": risk.get("probabilities", {}),
                "key_drivers": risk.get("top_features", []),
                "business_explanation": risk.get(
                    "business_explanation",
                    "No active risk model explanation available.",
                ),
                "source": "Random Forest risk model and feature importance",
            },
            "behaviour_analysis": {
                "summary": behaviour.get("summary", "No behaviour profile available."),
                "lifestyle_indicators": behaviour.get("lifestyle_indicators", []),
                "transaction_behaviour": behaviour.get("flags", []),
                "income_consistency": behaviour.get("features", {}).get(
                    "income_consistency",
                    "Unavailable",
                ),
                "spending_habits": behaviour.get("category_spend", {}),
                "financial_patterns": behaviour.get("features", {}),
                "source": "Deterministic transaction NLP and behaviour rules",
            },
            "product_recommendations": recommendations,
            "policy_validation": {
                "retrieved_chunks": policy.get("retrieved_chunks", 0),
                "citations": policy.get("citations", []),
                "eligibility_reasoning": self._policy_reasoning(policy),
                "source": "RAG policy retrieval",
            },
            "ai_summary": {
                "narrative": ai_summary,
                "provider": provider,
                "model": model,
                "prompt_version": prompt_version,
                "status": status,
            },
            "explainability": {
                "evidence": evidence,
                "confidence": self._section_confidence([confidence, 0.85]),
                "sources": [
                    "feature_store",
                    "ml_model_registry",
                    "transaction_insights",
                    "behaviour_profiles",
                    "recommendations",
                    "knowledge_chunks",
                ],
                "feature_importance": risk.get("top_features", []),
                "retrieved_chunks": policy.get("chunks", []),
            },
        }

    def _context_payload(self, evidence: dict[str, Any]) -> dict[str, Any]:
        return {
            "customer": evidence["customer"],
            "features": evidence["feature_store"],
            "risk": evidence["risk"],
            "segment": evidence["segment"],
            "behaviour": evidence["behaviour"],
            "recommendations": evidence["recommendations"],
            "policy_citations": evidence["policy_evidence"]["citations"],
        }

    def _row_response(
        self,
        row: CustomerIntelligenceReport,
        *,
        cache_hit: bool,
    ) -> dict[str, Any]:
        return {
            "id": row.id,
            "customer_id": row.customer_id,
            "report_version": row.report_version,
            "status": row.status,
            "report": row.report,
            "evidence": row.evidence,
            "workflow_trace": row.workflow_trace,
            "provider": row.provider,
            "model": row.model,
            "prompt_version": row.prompt_version,
            "latency_ms": row.latency_ms,
            "token_usage": {
                "prompt_tokens": row.prompt_tokens,
                "completion_tokens": row.completion_tokens,
                "total_tokens": row.total_tokens,
            },
            "retrieved_chunks": row.retrieved_chunks,
            "context_size": row.context_size,
            "cache_hit": cache_hit,
            "cache_hits": row.cache_hits,
            "generated_at": row.generated_at,
            "updated_at": row.updated_at,
        }

    def _cached(
        self,
        customer_id: str,
        input_hash: str,
    ) -> CustomerIntelligenceReport | None:
        return self.session.scalar(
            select(CustomerIntelligenceReport)
            .where(
                CustomerIntelligenceReport.customer_id == customer_id,
                CustomerIntelligenceReport.input_hash == input_hash,
            )
            .order_by(CustomerIntelligenceReport.generated_at.desc())
            .limit(1)
        )

    def _latest(self, customer_id: str) -> CustomerIntelligenceReport | None:
        return self.session.scalar(
            select(CustomerIntelligenceReport)
            .where(CustomerIntelligenceReport.customer_id == customer_id)
            .order_by(CustomerIntelligenceReport.generated_at.desc())
            .limit(1)
        )

    def _input_hash(
        self,
        *,
        customer: Customer,
        snapshot: FeatureSnapshot | None,
        risk: RiskPredictionResult | None,
        segment: SegmentPredictionResult | None,
        behaviour: BehaviourProfile | None,
        recommendations: list[Recommendation],
        citations: list[Citation],
        provider: str,
        model: str,
    ) -> str:
        payload = {
            "customer": {
                "id": customer.customer_id,
                "updated_at": customer.updated_at.isoformat(),
            },
            "feature": {
                "version": snapshot.feature_version if snapshot else None,
                "dataset": snapshot.dataset_version if snapshot else None,
                "generated_at": snapshot.generated_at.isoformat() if snapshot else None,
            },
            "risk_model": risk.model_version if risk else None,
            "segment_model": segment.model_version if segment else None,
            "behaviour": behaviour.generated_at.isoformat() if behaviour else None,
            "recommendations": [
                {
                    "id": row.id,
                    "score": row.suitability_score,
                    "generated_at": row.generated_at.isoformat(),
                }
                for row in recommendations
            ],
            "citations": [citation.__dict__ for citation in citations],
            "provider": provider,
            "model": model,
            "report_version": REPORT_VERSION,
        }
        encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def _risk_payload(self, risk: RiskPredictionResult | None) -> dict[str, Any]:
        if risk is None:
            return {"risk_level": "Unavailable", "confidence": 0.0}
        return {
            "risk_level": risk.risk_level,
            "confidence": risk.confidence,
            "probabilities": risk.probabilities,
            "top_features": [
                {
                    "name": feature.name,
                    "value": feature.value,
                    "importance": feature.importance,
                    "description": feature.description,
                }
                for feature in risk.top_features
            ],
            "business_explanation": risk.business_explanation,
            "model_version": risk.model_version,
            "inference_time_ms": risk.inference_time_ms,
        }

    def _segment_payload(
        self,
        segment: SegmentPredictionResult | None,
    ) -> dict[str, Any]:
        if segment is None:
            return {"segment_label": "Unavailable", "confidence": 0.0}
        return {
            "segment_label": segment.segment_label,
            "confidence": segment.confidence,
            "nearest_distance": segment.nearest_distance,
            "centroid_summary": segment.centroid_summary,
            "model_version": segment.model_version,
            "inference_time_ms": segment.inference_time_ms,
        }

    def _behaviour_payload(
        self,
        behaviour: BehaviourProfile | None,
        insights_count: int,
    ) -> dict[str, Any]:
        if behaviour is None:
            return {"summary": "Unavailable", "insights_count": insights_count}
        return {
            "summary": behaviour.summary,
            "flags": behaviour.flags,
            "lifestyle_indicators": behaviour.lifestyle_indicators,
            "category_spend": behaviour.category_spend,
            "category_counts": behaviour.category_counts,
            "monthly_trends": behaviour.monthly_trends,
            "top_merchants": behaviour.top_merchants,
            "features": behaviour.features,
            "profile_version": behaviour.profile_version,
            "generated_at": behaviour.generated_at.isoformat(),
            "insights_count": insights_count,
        }

    def _recommendation_payload(self, recommendation: Recommendation) -> dict[str, Any]:
        return {
            "product_name": recommendation.product_name,
            "suitability_score": recommendation.suitability_score,
            "confidence": recommendation.confidence,
            "reason": recommendation.reason,
            "supporting_features": recommendation.supporting_features,
            "business_explanation": recommendation.business_explanation,
            "source": "Rules-based recommendation engine",
        }

    def _citation(self, result: RetrievalResult) -> Citation:
        return Citation(
            document=result.chunk.document_name,
            section=result.chunk.section,
            chunk=result.chunk.id,
            similarity_score=result.score,
        )

    def _deterministic_summary(
        self,
        context: dict[str, Any],
        provider: str,
        model: str,
    ) -> str:
        customer = self._dict_value(context.get("customer"))
        risk = self._dict_value(context.get("risk"))
        behaviour = self._dict_value(context.get("behaviour"))
        recommendations = self._list_value(context.get("recommendations"))
        products = ", ".join(
            str(row.get("product_name")) for row in recommendations[:3] if row
        )
        return (
            f"Provider {provider}/{model} is not configured, so this deterministic "
            "summary was generated from structured evidence. "
            f"{customer.get('full_name') or customer.get('customer_id')} has "
            f"risk level {risk.get('risk_level', 'Unavailable')} with confidence "
            f"{risk.get('confidence', 0)}. Behaviour summary: "
            f"{behaviour.get('summary', 'Unavailable')} Recommended products: "
            f"{products or 'none'}."
        )

    def _feature_values(self, snapshot: FeatureSnapshot | None) -> dict[str, Any]:
        if snapshot is None or not isinstance(snapshot.features, dict):
            return {}
        values = snapshot.features.get("values")
        return values if isinstance(values, dict) else {}

    def _policy_reasoning(self, policy: dict[str, Any]) -> str:
        citations = self._list_value(policy.get("citations"))
        if not citations:
            return "No policy evidence was retrieved; eligibility is not asserted."
        sections = ", ".join(
            f"{item.get('document')} / {item.get('section')}"
            for item in citations[:3]
            if isinstance(item, dict)
        )
        return (
            "Eligibility reasoning is grounded in retrieved policy sections: "
            f"{sections}."
        )

    def _citation_text(self, citations: list[Citation]) -> str:
        if not citations:
            return "No citations retrieved."
        return "\n".join(
            (
                f"[{index}] {citation.document} / {citation.section}; "
                f"chunk={citation.chunk}; score={citation.similarity_score}"
            )
            for index, citation in enumerate(citations, start=1)
        )

    def _provider_usage(self) -> list[dict[str, Any]]:
        rows = self.session.execute(
            select(AIMetricLog.provider, func.count(AIMetricLog.id))
            .group_by(AIMetricLog.provider)
            .order_by(desc(func.count(AIMetricLog.id)))
        )
        return [{"provider": provider, "count": count} for provider, count in rows]

    def _risk_count(self, level: str) -> int:
        logs = self.session.scalar(
            select(func.count())
            .select_from(MLModelRegistry)
            .where(MLModelRegistry.model_name == "risk_prediction")
        )
        if not logs:
            return 0
        reports = self.session.scalars(select(CustomerIntelligenceReport)).all()
        return sum(
            1
            for row in reports
            if self._dict_value(row.report.get("risk_assessment")).get("current_risk")
            == level
        )

    def _segment_counts(self) -> list[dict[str, Any]]:
        reports = self.session.scalars(select(CustomerIntelligenceReport)).all()
        counts: dict[str, int] = {}
        for row in reports:
            label = str(
                self._dict_value(row.evidence.get("segment")).get(
                    "segment_label",
                    "Unavailable",
                )
            )
            counts[label] = counts.get(label, 0) + 1
        return [{"label": key, "value": value} for key, value in sorted(counts.items())]

    def _cache_trace(
        self,
        trace: list[dict[str, Any]],
        started: float,
    ) -> list[dict[str, Any]]:
        return [
            *trace,
            {
                "stage": "Report Cache",
                "source": "customer_intelligence_reports",
                "status": "cache_hit",
                "duration_ms": round((perf_counter() - started) * 1000, 2),
                "details": "Cached report returned without regeneration",
            },
        ]

    def _markdown(self, row: CustomerIntelligenceReport) -> str:
        report = row.report
        risk = self._dict_value(report.get("risk_assessment"))
        behaviour = self._dict_value(report.get("behaviour_analysis"))
        ai_summary = self._dict_value(report.get("ai_summary"))
        recommendations = self._list_value(report.get("product_recommendations"))
        policy = self._dict_value(report.get("policy_validation"))
        lines = [
            "# Customer Intelligence Report",
            "",
            f"- Customer ID: {row.customer_id}",
            f"- Generated: {row.generated_at.isoformat()}",
            f"- Provider: {row.provider}",
            f"- Model: {row.model}",
            "",
            "## Executive Summary",
            self._dict_value(report.get("executive_summary")).get(
                "overall_assessment",
                "",
            ),
            "",
            "## Risk Assessment",
            f"Risk: {risk.get('current_risk')} ({risk.get('confidence')})",
            str(risk.get("business_explanation", "")),
            "",
            "## Behaviour Analysis",
            str(behaviour.get("summary", "")),
            "",
            "## Product Recommendations",
        ]
        for item in recommendations:
            item_dict = self._dict_value(item)
            lines.append(
                f"- {item_dict.get('product_name')}: "
                f"{item_dict.get('reason')} "
                f"(score {item_dict.get('suitability_score')})"
            )
        lines.extend(["", "## Policy Citations"])
        for citation in self._list_value(policy.get("citations")):
            citation_dict = self._dict_value(citation)
            lines.append(
                f"- {citation_dict.get('document')} / "
                f"{citation_dict.get('section')} "
                f"(chunk {citation_dict.get('chunk')}, "
                f"score {citation_dict.get('similarity_score')})"
            )
        lines.extend(["", "## AI Summary", str(ai_summary.get("narrative", ""))])
        return "\n".join(lines)

    def _pdf(self, markdown: str) -> bytes:
        raw_lines: list[str] = []
        for line in markdown.splitlines():
            raw_lines.extend(textwrap.wrap(line, width=92) or [""])
        pages = [
            raw_lines[index : index + 44] for index in range(0, len(raw_lines), 44)
        ]
        objects: list[str] = ["<< /Type /Catalog /Pages 2 0 R >>"]
        page_refs: list[str] = []
        font_object_id = 3 + len(pages) * 2
        for page_index, lines in enumerate(pages):
            page_id = 3 + page_index * 2
            content_id = page_id + 1
            page_refs.append(f"{page_id} 0 R")
            objects.append(
                "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                f"/Resources << /Font << /F1 {font_object_id} 0 R >> >> "
                f"/Contents {content_id} 0 R >>"
            )
            content = self._pdf_content(lines)
            objects.append(
                f"<< /Length {len(content.encode('latin-1', errors='replace'))} >>\n"
                f"stream\n{content}\nendstream"
            )
        objects.insert(
            1, f"<< /Type /Pages /Kids [{' '.join(page_refs)}] /Count {len(pages)} >>"
        )
        objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        return self._pdf_bytes(objects)

    def _pdf_content(self, lines: list[str]) -> str:
        rows = ["BT", "/F1 10 Tf", "50 760 Td", "14 TL"]
        for line in lines:
            rows.append(f"({self._pdf_escape(line)}) Tj")
            rows.append("T*")
        rows.append("ET")
        return "\n".join(rows)

    def _pdf_bytes(self, objects: list[str]) -> bytes:
        output = ["%PDF-1.4\n"]
        offsets: list[int] = [0]
        current = len(output[0].encode("latin-1"))
        for index, body in enumerate(objects, start=1):
            offsets.append(current)
            chunk = f"{index} 0 obj\n{body}\nendobj\n"
            output.append(chunk)
            current += len(chunk.encode("latin-1", errors="replace"))
        xref_start = current
        output.append(f"xref\n0 {len(objects) + 1}\n")
        output.append("0000000000 65535 f \n")
        for offset in offsets[1:]:
            output.append(f"{offset:010d} 00000 n \n")
        output.append(
            "trailer\n"
            f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF\n"
        )
        return "".join(output).encode("latin-1", errors="replace")

    def _pdf_escape(self, value: str) -> str:
        return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    def _stage_details(self, result: object) -> str:
        if result is None:
            return "Unavailable"
        if isinstance(result, list):
            return f"{len(result)} records"
        return result.__class__.__name__

    def _section_confidence(self, values: list[float]) -> float:
        valid = [value for value in values if value > 0]
        if not valid:
            return 0.0
        return round(sum(valid) / len(valid), 4)

    def _dict_value(self, value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    def _list_value(self, value: Any) -> list[Any]:
        return value if isinstance(value, list) else []

    def _float(self, value: Any) -> float:
        return float(value) if isinstance(value, int | float) else 0.0
