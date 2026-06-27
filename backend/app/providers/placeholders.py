from __future__ import annotations

from collections.abc import AsyncIterator

from app.providers.base import (
    AIProvider,
    ProviderConfigurationError,
    ProviderHealth,
    ProviderModel,
    ProviderRequest,
    ProviderResponse,
)


class PlaceholderProvider(AIProvider):
    def __init__(self, provider_name: str) -> None:
        self.provider_name = provider_name

    def chat(self, request: ProviderRequest) -> ProviderResponse:
        msg = f"{self.provider_name} is registered as a future provider only."
        raise ProviderConfigurationError(msg)

    async def stream(self, request: ProviderRequest) -> AsyncIterator[str]:
        yield ""

    def health(self) -> ProviderHealth:
        return ProviderHealth(
            provider=self.provider_name,
            status="future_provider",
            configured=False,
            latency_ms=None,
            details="Provider placeholder for future extension.",
        )

    def list_models(self) -> list[ProviderModel]:
        return []


class GeminiProvider(PlaceholderProvider):
    def __init__(self) -> None:
        super().__init__("gemini")


class OllamaProvider(PlaceholderProvider):
    def __init__(self) -> None:
        super().__init__("ollama")


class AnthropicProvider(PlaceholderProvider):
    def __init__(self) -> None:
        super().__init__("anthropic")
