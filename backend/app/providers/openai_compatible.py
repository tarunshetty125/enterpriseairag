from __future__ import annotations

from collections.abc import AsyncIterator
from time import perf_counter
from typing import Any

import httpx

from app.providers.base import (
    AIProvider,
    ProviderConfigurationError,
    ProviderHealth,
    ProviderModel,
    ProviderRequest,
    ProviderResponse,
    TokenUsage,
)


class OpenAICompatibleProvider(AIProvider):
    """Provider adapter for OpenAI-compatible chat APIs."""

    def __init__(
        self,
        *,
        provider_name: str,
        base_url: str,
        api_key: str | None,
        default_models: tuple[ProviderModel, ...],
    ) -> None:
        self.provider_name = provider_name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.default_models = default_models

    def chat(self, request: ProviderRequest) -> ProviderResponse:
        if not self.api_key:
            msg = f"{self.provider_name} API key is not configured."
            raise ProviderConfigurationError(msg)
        payload = {
            "model": request.model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in request.messages
            ],
            "temperature": request.temperature,
            "top_p": request.top_p,
            "max_tokens": request.max_tokens,
        }
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            headers=self._headers(),
            timeout=45,
        )
        response.raise_for_status()
        data = response.json()
        choices = self._list_value(data.get("choices"))
        content = ""
        if choices:
            first = self._dict_value(choices[0])
            message = self._dict_value(first.get("message"))
            content = str(message.get("content", ""))
        usage = self._usage(data.get("usage"))
        return ProviderResponse(
            content=content,
            model=str(data.get("model", request.model)),
            usage=usage,
            raw=self._dict_value(data),
        )

    async def stream(self, request: ProviderRequest) -> AsyncIterator[str]:
        response = self.chat(request)
        yield response.content

    def health(self) -> ProviderHealth:
        if not self.api_key:
            return ProviderHealth(
                provider=self.provider_name,
                status="not_configured",
                configured=False,
                latency_ms=None,
                details="API key not configured.",
            )
        started = perf_counter()
        try:
            models = self.list_models()
        except Exception as exc:  # pragma: no cover - network failure detail varies
            return ProviderHealth(
                provider=self.provider_name,
                status="offline",
                configured=True,
                latency_ms=round((perf_counter() - started) * 1000, 2),
                details=str(exc),
            )
        return ProviderHealth(
            provider=self.provider_name,
            status="online",
            configured=True,
            latency_ms=round((perf_counter() - started) * 1000, 2),
            details=f"{len(models)} models available.",
        )

    def list_models(self) -> list[ProviderModel]:
        if not self.api_key:
            return list(self.default_models)
        try:
            response = httpx.get(
                f"{self.base_url}/models",
                headers=self._headers(),
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
            rows = self._list_value(data.get("data"))
            models = [
                ProviderModel(
                    id=str(row.get("id")),
                    name=str(row.get("id")),
                    supports_streaming=True,
                )
                for row in (self._dict_value(item) for item in rows)
                if row.get("id")
            ]
            return sorted(models, key=lambda model: model.id) or list(
                self.default_models
            )
        except Exception:
            return list(self.default_models)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _usage(self, value: Any) -> TokenUsage:
        usage = self._dict_value(value)
        prompt = int(usage.get("prompt_tokens", 0) or 0)
        completion = int(usage.get("completion_tokens", 0) or 0)
        total = int(usage.get("total_tokens", prompt + completion) or 0)
        return TokenUsage(
            prompt_tokens=prompt,
            completion_tokens=completion,
            total_tokens=total,
        )

    def _dict_value(self, value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return value
        return {}

    def _list_value(self, value: Any) -> list[Any]:
        if isinstance(value, list):
            return value
        return []
