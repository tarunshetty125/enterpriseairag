from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.canonical import utc_now


class AIProviderSetting(Base):
    __tablename__ = "ai_provider_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    model: Mapped[str] = mapped_column(String(160), nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    top_p: Mapped[float] = mapped_column(Float, nullable=False)
    top_k: Mapped[int] = mapped_column(Integer, nullable=False)
    max_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_size: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(160), nullable=False)
    retrieval_top_k: Mapped[int] = mapped_column(Integer, nullable=False)
    similarity_threshold: Mapped[float] = mapped_column(Float, nullable=False)
    conversation_memory: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )


class ProviderSwitchEvent(Base):
    __tablename__ = "provider_switch_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    previous_provider: Mapped[str | None] = mapped_column(String(80), nullable=True)
    previous_model: Mapped[str | None] = mapped_column(String(160), nullable=True)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    model: Mapped[str] = mapped_column(String(160), nullable=False)
    reason: Mapped[str] = mapped_column(String(160), default="runtime_switch")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )


class AIMetricLog(Base):
    __tablename__ = "ai_metric_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(160), nullable=False)
    operation: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    retrieved_chunks: Mapped[int] = mapped_column(Integer, default=0)
    context_size: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    document_type: Mapped[str] = mapped_column(String(80), nullable=False)
    source_path: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(String(80), nullable=False)
    checksum: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    indexed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_knowledge_chunk"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    document_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    section: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    embedding_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    model: Mapped[str] = mapped_column(String(160), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(40), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    retrieved_context: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    citations: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    provider: Mapped[str | None] = mapped_column(String(80), nullable=True)
    model: Mapped[str | None] = mapped_column(String(160), nullable=True)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    token_usage: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
