"""Create NLP intelligence and recommendation schema.

Revision ID: 20260627_002
Revises: 20260627_001
Create Date: 2026-06-27 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260627_002"
down_revision: str | None = "20260627_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "transaction_insights",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("transaction_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.String(length=32), nullable=False),
        sa.Column("raw_description", sa.String(length=240), nullable=False),
        sa.Column("cleaned_description", sa.String(length=240), nullable=False),
        sa.Column("normalized_description", sa.String(length=240), nullable=False),
        sa.Column("keywords", sa.JSON(), nullable=False),
        sa.Column("entities", sa.JSON(), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("sentiment_label", sa.String(length=40), nullable=False),
        sa.Column("sentiment_score", sa.Float(), nullable=False),
        sa.Column("lifestyle_indicators", sa.JSON(), nullable=False),
        sa.Column("processing_version", sa.String(length=40), nullable=False),
        sa.Column("processing_time_ms", sa.Float(), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transaction_id"),
    )
    op.create_index(
        op.f("ix_transaction_insights_category"),
        "transaction_insights",
        ["category"],
        unique=False,
    )
    op.create_index(
        op.f("ix_transaction_insights_customer_id"),
        "transaction_insights",
        ["customer_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_transaction_insights_transaction_id"),
        "transaction_insights",
        ["transaction_id"],
        unique=False,
    )
    op.create_table(
        "behaviour_profiles",
        sa.Column("customer_id", sa.String(length=32), nullable=False),
        sa.Column("profile_version", sa.String(length=40), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("flags", sa.JSON(), nullable=False),
        sa.Column("lifestyle_indicators", sa.JSON(), nullable=False),
        sa.Column("category_spend", sa.JSON(), nullable=False),
        sa.Column("category_counts", sa.JSON(), nullable=False),
        sa.Column("monthly_trends", sa.JSON(), nullable=False),
        sa.Column("top_merchants", sa.JSON(), nullable=False),
        sa.Column("features", sa.JSON(), nullable=False),
        sa.Column("processing_time_ms", sa.Float(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.customer_id"]),
        sa.PrimaryKeyConstraint("customer_id"),
    )
    op.create_table(
        "recommendation_rules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("rule_id", sa.String(length=80), nullable=False),
        sa.Column("product_name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("conditions", sa.JSON(), nullable=False),
        sa.Column("base_score", sa.Float(), nullable=False),
        sa.Column("version", sa.String(length=40), nullable=False),
        sa.Column("active", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("rule_id"),
    )
    op.create_index(
        op.f("ix_recommendation_rules_active"),
        "recommendation_rules",
        ["active"],
        unique=False,
    )
    op.create_index(
        op.f("ix_recommendation_rules_product_name"),
        "recommendation_rules",
        ["product_name"],
        unique=False,
    )
    op.create_table(
        "recommendations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("customer_id", sa.String(length=32), nullable=False),
        sa.Column("rule_id", sa.String(length=80), nullable=False),
        sa.Column("product_name", sa.String(length=120), nullable=False),
        sa.Column("suitability_score", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("supporting_features", sa.JSON(), nullable=False),
        sa.Column("business_explanation", sa.Text(), nullable=False),
        sa.Column("recommendation_version", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_recommendations_customer_id"),
        "recommendations",
        ["customer_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_recommendations_rule_id"),
        "recommendations",
        ["rule_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_recommendations_status"),
        "recommendations",
        ["status"],
        unique=False,
    )
    op.create_table(
        "recommendation_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("customer_id", sa.String(length=32), nullable=False),
        sa.Column("recommendation_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["recommendation_id"], ["recommendations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_recommendation_history_customer_id"),
        "recommendation_history",
        ["customer_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_recommendation_history_customer_id"),
        table_name="recommendation_history",
    )
    op.drop_table("recommendation_history")
    op.drop_index(op.f("ix_recommendations_status"), table_name="recommendations")
    op.drop_index(op.f("ix_recommendations_rule_id"), table_name="recommendations")
    op.drop_index(
        op.f("ix_recommendations_customer_id"),
        table_name="recommendations",
    )
    op.drop_table("recommendations")
    op.drop_index(
        op.f("ix_recommendation_rules_product_name"),
        table_name="recommendation_rules",
    )
    op.drop_index(
        op.f("ix_recommendation_rules_active"),
        table_name="recommendation_rules",
    )
    op.drop_table("recommendation_rules")
    op.drop_table("behaviour_profiles")
    op.drop_index(
        op.f("ix_transaction_insights_transaction_id"),
        table_name="transaction_insights",
    )
    op.drop_index(
        op.f("ix_transaction_insights_customer_id"),
        table_name="transaction_insights",
    )
    op.drop_index(
        op.f("ix_transaction_insights_category"),
        table_name="transaction_insights",
    )
    op.drop_table("transaction_insights")
