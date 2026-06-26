"""Create machine learning registry schema.

Revision ID: 20260627_001
Revises: 20260626_001
Create Date: 2026-06-27 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260627_001"
down_revision: str | None = "20260626_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ml_model_registry",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("model_name", sa.String(length=120), nullable=False),
        sa.Column("version", sa.String(length=80), nullable=False),
        sa.Column("algorithm", sa.String(length=120), nullable=False),
        sa.Column("training_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("accuracy", sa.Float(), nullable=True),
        sa.Column("precision", sa.Float(), nullable=True),
        sa.Column("recall", sa.Float(), nullable=True),
        sa.Column("f1", sa.Float(), nullable=True),
        sa.Column("features_used", sa.JSON(), nullable=False),
        sa.Column("artifact_path", sa.Text(), nullable=False),
        sa.Column("dataset_version", sa.String(length=80), nullable=False),
        sa.Column("feature_version", sa.String(length=40), nullable=False),
        sa.Column("active_model", sa.Integer(), nullable=False),
        sa.Column("training_time_ms", sa.Float(), nullable=False),
        sa.Column("inference_time_ms", sa.Float(), nullable=True),
        sa.Column("training_metadata", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("model_name", "version", name="uq_ml_model_name_version"),
    )
    op.create_index(
        op.f("ix_ml_model_registry_active_model"),
        "ml_model_registry",
        ["active_model"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ml_model_registry_model_name"),
        "ml_model_registry",
        ["model_name"],
        unique=False,
    )
    op.create_table(
        "ml_prediction_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("model_id", sa.Integer(), nullable=False),
        sa.Column("model_name", sa.String(length=120), nullable=False),
        sa.Column("model_version", sa.String(length=80), nullable=False),
        sa.Column("customer_id", sa.String(length=32), nullable=False),
        sa.Column("prediction", sa.String(length=80), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("inference_time_ms", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["model_id"], ["ml_model_registry.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_ml_prediction_logs_customer_id"),
        "ml_prediction_logs",
        ["customer_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ml_prediction_logs_model_id"),
        "ml_prediction_logs",
        ["model_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ml_prediction_logs_model_name"),
        "ml_prediction_logs",
        ["model_name"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_ml_prediction_logs_model_name"),
        table_name="ml_prediction_logs",
    )
    op.drop_index(
        op.f("ix_ml_prediction_logs_model_id"),
        table_name="ml_prediction_logs",
    )
    op.drop_index(
        op.f("ix_ml_prediction_logs_customer_id"), table_name="ml_prediction_logs"
    )
    op.drop_table("ml_prediction_logs")
    op.drop_index(
        op.f("ix_ml_model_registry_model_name"), table_name="ml_model_registry"
    )
    op.drop_index(
        op.f("ix_ml_model_registry_active_model"), table_name="ml_model_registry"
    )
    op.drop_table("ml_model_registry")
