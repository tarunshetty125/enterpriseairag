from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ai import AIMetricLog
from app.providers.base import TokenUsage


class MetricsCollector:
    """Persists AI gateway metrics for the Developer Console."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def record(
        self,
        *,
        provider: str,
        model: str,
        operation: str,
        latency_ms: float,
        usage: TokenUsage,
        retrieved_chunks: int,
        context_size: int,
        status: str,
        details: dict[str, object],
    ) -> AIMetricLog:
        row = AIMetricLog(
            provider=provider,
            model=model,
            operation=operation,
            latency_ms=latency_ms,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            retrieved_chunks=retrieved_chunks,
            context_size=context_size,
            status=status,
            details=details,
        )
        self.session.add(row)
        self.session.commit()
        return row

    def status(self) -> dict[str, int | float | str | None]:
        latest = self.session.scalar(
            select(AIMetricLog).order_by(AIMetricLog.created_at.desc()).limit(1)
        )
        average_latency = self.session.scalar(select(func.avg(AIMetricLog.latency_ms)))
        total_tokens = self.session.scalar(select(func.sum(AIMetricLog.total_tokens)))
        return {
            "latest_provider": latest.provider if latest else None,
            "latest_model": latest.model if latest else None,
            "latest_latency_ms": latest.latency_ms if latest else None,
            "average_latency_ms": round(float(average_latency or 0.0), 2),
            "total_tokens": int(total_tokens or 0),
            "latest_retrieved_chunks": latest.retrieved_chunks if latest else 0,
            "latest_context_size": latest.context_size if latest else 0,
            "metric_count": self.session.scalar(select(func.count(AIMetricLog.id)))
            or 0,
        }
