from __future__ import annotations

from app.providers.base import ProviderModel
from app.providers.openai_compatible import OpenAICompatibleProvider

GROQ_MODELS: tuple[ProviderModel, ...] = (
    ProviderModel(id="llama-3.3-70b-versatile", name="Llama 3.3 70B"),
    ProviderModel(id="deepseek-r1-distill-llama-70b", name="DeepSeek R1 Distill"),
    ProviderModel(id="qwen/qwen3-32b", name="Qwen 3 32B"),
    ProviderModel(id="mixtral-8x7b-32768", name="Mixtral 8x7B"),
)


class GroqProvider(OpenAICompatibleProvider):
    def __init__(self, *, base_url: str, api_key: str | None) -> None:
        super().__init__(
            provider_name="groq",
            base_url=base_url,
            api_key=api_key,
            default_models=GROQ_MODELS,
        )
