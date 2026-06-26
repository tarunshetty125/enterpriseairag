from __future__ import annotations

from pydantic import BaseModel, ConfigDict


def to_camel(value: str) -> str:
    words = value.split("_")
    return words[0] + "".join(word.capitalize() for word in words[1:])


class AIProcessingSettingsResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
        extra="forbid",
    )

    provider: str
    model: str
    temperature: float
    top_p: float
    top_k: int
    max_tokens: int
    chunk_size: int
    embedding_model: str
    conversation_memory: bool
