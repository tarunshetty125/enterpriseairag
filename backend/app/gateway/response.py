from __future__ import annotations

from dataclasses import dataclass

from app.providers.base import ProviderResponse, TokenUsage


@dataclass(frozen=True)
class NormalizedAIResponse:
    content: str
    model: str
    usage: TokenUsage
    raw: dict[str, object]


class ResponseNormalizer:
    """Converts provider responses into the gateway response contract."""

    def normalize(self, response: ProviderResponse) -> NormalizedAIResponse:
        return NormalizedAIResponse(
            content=response.content.strip(),
            model=response.model,
            usage=response.usage,
            raw=response.raw,
        )
