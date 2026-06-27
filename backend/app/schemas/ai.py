from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.settings import to_camel


class AIModelResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    name: str
    context_window: int | None
    supports_streaming: bool


class ProviderResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str
    status: str
    configured: bool
    active: bool
    latency_ms: float | None
    details: str


class ProviderListResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    providers: list[ProviderResponse]


class ProviderModelsResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    provider: str
    models: list[AIModelResponse]


class ProviderSwitchRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    provider: str
    model: str


class ProviderSettingsPatch(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    temperature: float | None = Field(default=None, ge=0, le=2)
    top_p: float | None = Field(default=None, ge=0, le=1)
    top_k: int | None = Field(default=None, ge=1, le=50)
    max_tokens: int | None = Field(default=None, ge=64, le=8000)
    chunk_size: int | None = Field(default=None, ge=200, le=4000)
    embedding_model: str | None = None
    retrieval_top_k: int | None = Field(default=None, ge=1, le=20)
    similarity_threshold: float | None = Field(default=None, ge=0, le=1)
    conversation_memory: bool | None = None


class AIProcessingSettingsResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
    )

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


class ProviderStatusResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    settings: AIProcessingSettingsResponse
    providers: list[ProviderResponse]
    metrics: dict[str, Any]
    switch_events: list[dict[str, Any]]


class KnowledgeDocumentResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    document_name: str
    document_type: str
    source_path: str
    version: str
    checksum: str
    status: str
    chunk_count: int
    indexed_at: datetime


class KnowledgeIngestResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    documents_indexed: int
    chunks_indexed: int
    embedding_backend: str
    vector_backend: str


class KnowledgeStatusResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    document_count: int
    chunk_count: int
    embedding_model: str
    embedding_backend: str
    vector_backend: str
    faiss_index_size: int
    dimensions: int
    latest_indexed_at: datetime | None


class CitationResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    document: str
    section: str
    chunk: int
    similarity_score: float


class ChatRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    message: str
    session_id: str | None = None
    customer_id: str | None = None


class TokenUsageResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    session_id: str
    answer: str
    citations: list[CitationResponse]
    provider: str
    model: str
    latency_ms: float
    token_usage: TokenUsageResponse
    retrieved_chunks: int
    context_size: int
    prompt_version: str
    status: str


class ChatSessionResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    session_id: str
    title: str
    provider: str
    model: str
    created_at: datetime
    updated_at: datetime


class ChatSessionDetailResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    session: ChatSessionResponse
    messages: list[dict[str, Any]]


class PromptResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str
    version: str
    description: str
    variables: list[str]
    body: str
