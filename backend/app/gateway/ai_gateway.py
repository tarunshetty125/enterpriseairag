from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any

from sqlalchemy.orm import Session

from app.gateway.metrics import MetricsCollector
from app.gateway.response import NormalizedAIResponse, ResponseNormalizer
from app.gateway.retry import RetryPolicy
from app.gateway.router import RequestRouter
from app.gateway.streaming import StreamingAdapter
from app.gateway.token_accounting import TokenAccounting
from app.providers.base import ProviderMessage, ProviderRequest, TokenUsage
from app.providers.manager import ProviderManager


@dataclass(frozen=True)
class GatewayRequest:
    messages: list[ProviderMessage]
    operation: str
    metadata: dict[str, Any]
    retrieved_chunks: int = 0
    context_size: int = 0


@dataclass(frozen=True)
class GatewayResponse:
    content: str
    provider: str
    model: str
    latency_ms: float
    usage: TokenUsage
    raw: dict[str, object]


class AIGateway:
    """Enterprise gateway for all LLM requests."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.router = RequestRouter(session)
        self.manager = ProviderManager(session)
        self.metrics = MetricsCollector(session)
        self.retry = RetryPolicy()
        self.streaming = StreamingAdapter()
        self.accounting = TokenAccounting()
        self.normalizer = ResponseNormalizer()

    def chat(self, request: GatewayRequest) -> GatewayResponse:
        settings = self.manager.current_settings()
        provider = self.router.active_provider()
        provider_request = ProviderRequest(
            messages=request.messages,
            model=settings.model,
            temperature=settings.temperature,
            top_p=settings.top_p,
            max_tokens=settings.max_tokens,
            metadata=request.metadata,
        )
        prompt_tokens = self.accounting.estimate_messages(request.messages)
        started = perf_counter()
        normalized: NormalizedAIResponse
        try:
            provider_response = self.retry.run(lambda: provider.chat(provider_request))
            normalized = self.normalizer.normalize(provider_response)
            usage = self.accounting.merge(
                prompt_tokens=prompt_tokens,
                completion_text=normalized.content,
                provider_usage=normalized.usage,
            )
            latency_ms = round((perf_counter() - started) * 1000, 2)
            self.metrics.record(
                provider=settings.provider,
                model=normalized.model,
                operation=request.operation,
                latency_ms=latency_ms,
                usage=usage,
                retrieved_chunks=request.retrieved_chunks,
                context_size=request.context_size,
                status="success",
                details=request.metadata,
            )
            return GatewayResponse(
                content=normalized.content,
                provider=settings.provider,
                model=normalized.model,
                latency_ms=latency_ms,
                usage=usage,
                raw=normalized.raw,
            )
        except Exception as exc:
            latency_ms = round((perf_counter() - started) * 1000, 2)
            usage = TokenUsage(prompt_tokens=prompt_tokens, total_tokens=prompt_tokens)
            self.metrics.record(
                provider=settings.provider,
                model=settings.model,
                operation=request.operation,
                latency_ms=latency_ms,
                usage=usage,
                retrieved_chunks=request.retrieved_chunks,
                context_size=request.context_size,
                status="error",
                details={"error": str(exc), **request.metadata},
            )
            raise
