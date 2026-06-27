"""Create AI gateway, knowledge, and chat memory schema.

Revision ID: 20260627_003
Revises: 20260627_002
Create Date: 2026-06-27 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260627_003"
down_revision: str | None = "20260627_002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_provider_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("model", sa.String(length=160), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=False),
        sa.Column("top_p", sa.Float(), nullable=False),
        sa.Column("top_k", sa.Integer(), nullable=False),
        sa.Column("max_tokens", sa.Integer(), nullable=False),
        sa.Column("chunk_size", sa.Integer(), nullable=False),
        sa.Column("embedding_model", sa.String(length=160), nullable=False),
        sa.Column("retrieval_top_k", sa.Integer(), nullable=False),
        sa.Column("similarity_threshold", sa.Float(), nullable=False),
        sa.Column("conversation_memory", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "provider_switch_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("previous_provider", sa.String(length=80), nullable=True),
        sa.Column("previous_model", sa.String(length=160), nullable=True),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("model", sa.String(length=160), nullable=False),
        sa.Column("reason", sa.String(length=160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ai_metric_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("model", sa.String(length=160), nullable=False),
        sa.Column("operation", sa.String(length=80), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False),
        sa.Column("completion_tokens", sa.Integer(), nullable=False),
        sa.Column("total_tokens", sa.Integer(), nullable=False),
        sa.Column("retrieved_chunks", sa.Integer(), nullable=False),
        sa.Column("context_size", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_ai_metric_logs_operation"),
        "ai_metric_logs",
        ["operation"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_metric_logs_provider"),
        "ai_metric_logs",
        ["provider"],
        unique=False,
    )
    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("document_name", sa.String(length=200), nullable=False),
        sa.Column("document_type", sa.String(length=80), nullable=False),
        sa.Column("source_path", sa.Text(), nullable=False),
        sa.Column("version", sa.String(length=80), nullable=False),
        sa.Column("checksum", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.Column("chunk_count", sa.Integer(), nullable=False),
        sa.Column("indexed_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_name"),
    )
    op.create_table(
        "knowledge_chunks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("document_name", sa.String(length=200), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("section", sa.String(length=200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False),
        sa.Column("embedding_metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_id", "chunk_index", name="uq_knowledge_chunk"),
    )
    op.create_index(
        op.f("ix_knowledge_chunks_document_id"),
        "knowledge_chunks",
        ["document_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_chunks_document_name"),
        "knowledge_chunks",
        ["document_name"],
        unique=False,
    )
    op.create_table(
        "chat_sessions",
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("model", sa.String(length=160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("session_id"),
    )
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("role", sa.String(length=40), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("retrieved_context", sa.JSON(), nullable=False),
        sa.Column("citations", sa.JSON(), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=True),
        sa.Column("model", sa.String(length=160), nullable=True),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column("token_usage", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_chat_messages_session_id"),
        "chat_messages",
        ["session_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_chat_messages_session_id"), table_name="chat_messages")
    op.drop_table("chat_messages")
    op.drop_table("chat_sessions")
    op.drop_index(op.f("ix_knowledge_chunks_document_name"), table_name="knowledge_chunks")
    op.drop_index(op.f("ix_knowledge_chunks_document_id"), table_name="knowledge_chunks")
    op.drop_table("knowledge_chunks")
    op.drop_table("knowledge_documents")
    op.drop_index(op.f("ix_ai_metric_logs_provider"), table_name="ai_metric_logs")
    op.drop_index(op.f("ix_ai_metric_logs_operation"), table_name="ai_metric_logs")
    op.drop_table("ai_metric_logs")
    op.drop_table("provider_switch_events")
    op.drop_table("ai_provider_settings")
