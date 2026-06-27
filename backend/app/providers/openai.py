"""OpenAI provider adapter.

Extends OpenAICompatibleProvider with OpenAI-specific defaults.
Uses the standard OpenAI API at https://api.openai.com/v1.
"""

from __future__ import annotations

from app.providers.base import ProviderModel
from app.providers.openai_compatible import OpenAICompatibleProvider

OPENAI_MODELS: tuple[ProviderModel, ...] = (
    ProviderModel(id="gpt-4.1", name="GPT-4.1"),
    ProviderModel(id="gpt-4o", name="GPT-4o"),
    ProviderModel(id="gpt-5", name="GPT-5"),
    ProviderModel(id="o3-mini", name="o3 Mini"),
)


class OpenAIProvider(OpenAICompatibleProvider):
    def __init__(self, *, base_url: str, api_key: str | None) -> None:
        super().__init__(
            provider_name="openai",
            base_url=base_url,
            api_key=api_key,
            default_models=OPENAI_MODELS,
        )
