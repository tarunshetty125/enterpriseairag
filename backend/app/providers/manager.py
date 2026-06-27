from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.ai import AIProviderSetting, ProviderSwitchEvent
from app.models.canonical import utc_now
from app.providers.base import AIProvider, ProviderModel
from app.providers.groq import GroqProvider
from app.providers.openai import OpenAIProvider
from app.providers.placeholders import AnthropicProvider, GeminiProvider, OllamaProvider


@dataclass(frozen=True)
class AIProcessingSettings:
    provider: str
    model: str
    temperature: float
    top_p: float
    top_k: int
    max_tokens: int
    chunk_size: int
    embedding_model: str
    retrieval_top_k: int
    similarity_threshold: float
    conversation_memory: bool


@dataclass(frozen=True)
class ProviderDescriptor:
    name: str
    status: str
    configured: bool
    active: bool
    latency_ms: float | None
    details: str


class ProviderManager:
    """Owns runtime AI provider selection and provider discovery."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.settings = get_settings().ai
        self.providers = self._providers()

    def current_settings(self) -> AIProcessingSettings:
        row = self._settings_row()
        return AIProcessingSettings(
            provider=row.provider,
            model=row.model,
            temperature=row.temperature,
            top_p=row.top_p,
            top_k=row.top_k,
            max_tokens=row.max_tokens,
            chunk_size=row.chunk_size,
            embedding_model=row.embedding_model,
            retrieval_top_k=row.retrieval_top_k,
            similarity_threshold=row.similarity_threshold,
            conversation_memory=bool(row.conversation_memory),
        )

    def list_providers(self) -> list[ProviderDescriptor]:
        current = self.current_settings()
        descriptors: list[ProviderDescriptor] = []
        for name, provider in sorted(self.providers.items()):
            health = provider.health()
            descriptors.append(
                ProviderDescriptor(
                    name=name,
                    status=health.status,
                    configured=health.configured,
                    active=name == current.provider,
                    latency_ms=health.latency_ms,
                    details=health.details,
                )
            )
        return descriptors

    def list_models(self, provider_name: str | None = None) -> list[ProviderModel]:
        provider = self.provider(provider_name or self.current_settings().provider)
        return provider.list_models()

    def provider(self, provider_name: str) -> AIProvider:
        provider = self.providers.get(provider_name)
        if provider is None:
            msg = f"Unknown AI provider: {provider_name}"
            raise ValueError(msg)
        return provider

    def active_provider(self) -> AIProvider:
        return self.provider(self.current_settings().provider)

    def switch_provider(self, provider: str, model: str) -> AIProcessingSettings:
        if provider not in self.providers:
            msg = f"Unknown AI provider: {provider}"
            raise ValueError(msg)
        models = {item.id for item in self.list_models(provider)}
        if models and model not in models:
            msg = f"Model {model} is not available for provider {provider}."
            raise ValueError(msg)
        row = self._settings_row()
        previous_provider = row.provider
        previous_model = row.model
        row.provider = provider
        row.model = model
        row.updated_at = utc_now()
        self.session.add(
            ProviderSwitchEvent(
                previous_provider=previous_provider,
                previous_model=previous_model,
                provider=provider,
                model=model,
            )
        )
        self.session.commit()
        return self.current_settings()

    def update_settings(
        self,
        *,
        temperature: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        max_tokens: int | None = None,
        chunk_size: int | None = None,
        embedding_model: str | None = None,
        retrieval_top_k: int | None = None,
        similarity_threshold: float | None = None,
        conversation_memory: bool | None = None,
    ) -> AIProcessingSettings:
        row = self._settings_row()
        if temperature is not None:
            row.temperature = temperature
        if top_p is not None:
            row.top_p = top_p
        if top_k is not None:
            row.top_k = top_k
        if max_tokens is not None:
            row.max_tokens = max_tokens
        if chunk_size is not None:
            row.chunk_size = chunk_size
        if embedding_model is not None:
            row.embedding_model = embedding_model
        if retrieval_top_k is not None:
            row.retrieval_top_k = retrieval_top_k
        if similarity_threshold is not None:
            row.similarity_threshold = similarity_threshold
        if conversation_memory is not None:
            row.conversation_memory = int(conversation_memory)
        row.updated_at = utc_now()
        self.session.commit()
        return self.current_settings()

    def latest_switches(self, limit: int = 10) -> list[ProviderSwitchEvent]:
        return list(
            self.session.scalars(
                select(ProviderSwitchEvent)
                .order_by(ProviderSwitchEvent.created_at.desc())
                .limit(limit)
            )
        )

    def switch_count(self) -> int:
        return self.session.scalar(select(func.count(ProviderSwitchEvent.id))) or 0

    def _settings_row(self) -> AIProviderSetting:
        row = self.session.get(AIProviderSetting, 1)
        if row is not None:
            return row
        row = AIProviderSetting(
            id=1,
            provider=self.settings.provider,
            model=self.settings.model,
            temperature=self.settings.temperature,
            top_p=self.settings.top_p,
            top_k=self.settings.top_k,
            max_tokens=self.settings.max_tokens,
            chunk_size=self.settings.chunk_size,
            embedding_model=self.settings.embedding_model,
            retrieval_top_k=self.settings.retrieval_top_k,
            similarity_threshold=self.settings.similarity_threshold,
            conversation_memory=int(self.settings.conversation_memory),
        )
        self.session.add(row)
        self.session.commit()
        return row

    def _providers(self) -> dict[str, AIProvider]:
        return {
            "groq": GroqProvider(
                base_url=self.settings.groq_base_url,
                api_key=self.settings.groq_api_key,
            ),
            "openai": OpenAIProvider(
                base_url=self.settings.openai_base_url,
                api_key=self.settings.openai_api_key,
            ),
            "gemini": GeminiProvider(),
            "ollama": OllamaProvider(),
            "anthropic": AnthropicProvider(),
        }
