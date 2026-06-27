"""Create final customer intelligence report cache.

Revision ID: 20260627_004
Revises: 20260627_003
Create Date: 2026-06-27 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260627_004"
down_revision: str | None = "20260627_003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "customer_intelligence_reports",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("customer_id", sa.String(length=32), nullable=False),
        sa.Column("report_version", sa.String(length=40), nullable=False),
        sa.Column("input_hash", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.Column("report", sa.JSON(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("workflow_trace", sa.JSON(), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("model", sa.String(length=160), nullable=False),
        sa.Column("prompt_version", sa.String(length=80), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False),
        sa.Column("completion_tokens", sa.Integer(), nullable=False),
        sa.Column("total_tokens", sa.Integer(), nullable=False),
        sa.Column("retrieved_chunks", sa.Integer(), nullable=False),
        sa.Column("context_size", sa.Integer(), nullable=False),
        sa.Column("cache_hits", sa.Integer(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_customer_intelligence_reports_customer_id"),
        "customer_intelligence_reports",
        ["customer_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_customer_intelligence_reports_input_hash"),
        "customer_intelligence_reports",
        ["input_hash"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_customer_intelligence_reports_input_hash"),
        table_name="customer_intelligence_reports",
    )
    op.drop_index(
        op.f("ix_customer_intelligence_reports_customer_id"),
        table_name="customer_intelligence_reports",
    )
    op.drop_table("customer_intelligence_reports")
