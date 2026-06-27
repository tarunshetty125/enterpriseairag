from __future__ import annotations

from collections.abc import AsyncIterator

from app.providers.base import AIProvider, ProviderRequest


class StreamingAdapter:
    """Keeps streaming behind the same provider interface."""

    async def stream(
        self,
        provider: AIProvider,
        request: ProviderRequest,
    ) -> AsyncIterator[str]:
        async for chunk in provider.stream(request):
            yield chunk
