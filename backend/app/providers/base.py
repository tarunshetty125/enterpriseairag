from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProviderMessage:
    role: str
    content: str


@dataclass(frozen=True)
class ProviderModel:
    id: str
    name: str
    context_window: int | None = None
    supports_streaming: bool = True


@dataclass(frozen=True)
class ProviderHealth:
    provider: str
    status: str
    configured: bool
    latency_ms: float | None
    details: str


@dataclass(frozen=True)
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass(frozen=True)
class ProviderRequest:
    messages: list[ProviderMessage]
    model: str
    temperature: float
    top_p: float
    max_tokens: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderResponse:
    content: str
    model: str
    usage: TokenUsage
    raw: dict[str, Any]


class ProviderConfigurationError(RuntimeError):
    """Raised when a provider is selected but not configured."""


class AIProvider(ABC):
    provider_name: str

    @abstractmethod
    def chat(self, request: ProviderRequest) -> ProviderResponse:
        """Generate a chat response."""

    @abstractmethod
    def stream(self, request: ProviderRequest) -> AsyncIterator[str]:
        """Stream a chat response."""

    @abstractmethod
    def health(self) -> ProviderHealth:
        """Return provider health and configuration status."""

    @abstractmethod
    def list_models(self) -> list[ProviderModel]:
        """Return models available for this provider."""
