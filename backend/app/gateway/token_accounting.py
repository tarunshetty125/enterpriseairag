from __future__ import annotations

from app.providers.base import ProviderMessage, TokenUsage


class TokenAccounting:
    """Lightweight token accounting with provider usage fallback."""

    def estimate_messages(self, messages: list[ProviderMessage]) -> int:
        return sum(self.estimate_text(message.content) for message in messages)

    def estimate_text(self, text: str) -> int:
        if not text:
            return 0
        return max(1, len(text.split()))

    def merge(
        self,
        *,
        prompt_tokens: int,
        completion_text: str,
        provider_usage: TokenUsage,
    ) -> TokenUsage:
        if provider_usage.total_tokens > 0:
            return provider_usage
        completion_tokens = self.estimate_text(completion_text)
        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )
