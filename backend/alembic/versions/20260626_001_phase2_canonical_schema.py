"""Create canonical financial data schema.

Revision ID: 20260626_001
Revises:
Create Date: 2026-06-26 19:59:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260626_001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("customer_id", sa.String(length=32), nullable=False),
        sa.Column("full_name", sa.String(length=160), nullable=True),
        sa.Column("gender", sa.String(length=32), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("geography", sa.String(length=80), nullable=True),
        sa.Column("education", sa.String(length=80), nullable=True),
        sa.Column("marital_status", sa.String(length=80), nullable=True),
        sa.Column("income_category", sa.String(length=80), nullable=True),
        sa.Column("estimated_income", sa.Float(), nullable=True),
        sa.Column("credit_score", sa.Integer(), nullable=True),
        sa.Column("savings_balance", sa.Float(), nullable=True),
        sa.Column("tenure_months", sa.Integer(), nullable=True),
        sa.Column("source_dataset", sa.String(length=120), nullable=False),
        sa.Column("source_record_id", sa.String(length=160), nullable=False),
        sa.Column("external_references", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("customer_id"),
    )
    op.create_table(
        "dataset_metadata",
        sa.Column("dataset_name", sa.String(length=120), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("version", sa.String(length=80), nullable=False),
        sa.Column("rows", sa.Integer(), nullable=False),
        sa.Column("columns", sa.JSON(), nullable=False),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("checksum", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.PrimaryKeyConstraint("dataset_name"),
    )
    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("dataset_name", sa.String(length=120), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("rows_processed", sa.Integer(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_ingestion_runs_dataset_name"),
        "ingestion_runs",
        ["dataset_name"],
        unique=False,
    )
    op.create_table(
        "loans",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("customer_id", sa.String(length=32), nullable=False),
        sa.Column("loan_type", sa.String(length=80), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("term_months", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("credit_history", sa.Float(), nullable=True),
        sa.Column("property_area", sa.String(length=80), nullable=True),
        sa.Column("source_dataset", sa.String(length=120), nullable=False),
        sa.Column("source_record_id", sa.String(length=160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.customer_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_dataset", "source_record_id", name="uq_loans_source_record"
        ),
    )
    op.create_index(
        op.f("ix_loans_customer_id"), "loans", ["customer_id"], unique=False
    )
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("customer_id", sa.String(length=32), nullable=False),
        sa.Column("product_type", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("credit_limit", sa.Float(), nullable=True),
        sa.Column("revolving_balance", sa.Float(), nullable=True),
        sa.Column("revenue", sa.Float(), nullable=False),
        sa.Column("source_dataset", sa.String(length=120), nullable=False),
        sa.Column("source_record_id", sa.String(length=160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.customer_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_dataset", "source_record_id", name="uq_products_source_record"
        ),
    )
    op.create_index(
        op.f("ix_products_customer_id"), "products", ["customer_id"], unique=False
    )
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("customer_id", sa.String(length=32), nullable=False),
        sa.Column("step", sa.Integer(), nullable=True),
        sa.Column("transaction_type", sa.String(length=80), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("direction", sa.String(length=20), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("description", sa.String(length=240), nullable=False),
        sa.Column("counterparty", sa.String(length=160), nullable=True),
        sa.Column("is_fraud", sa.Integer(), nullable=False),
        sa.Column("source_dataset", sa.String(length=120), nullable=False),
        sa.Column("source_record_id", sa.String(length=160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.customer_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_dataset",
            "source_record_id",
            name="uq_transactions_source_record",
        ),
    )
    op.create_index(
        op.f("ix_transactions_customer_id"),
        "transactions",
        ["customer_id"],
        unique=False,
    )
    op.create_table(
        "feature_snapshots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("customer_id", sa.String(length=32), nullable=False),
        sa.Column("feature_version", sa.String(length=40), nullable=False),
        sa.Column("dataset_version", sa.String(length=80), nullable=False),
        sa.Column("features", sa.JSON(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.customer_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "customer_id",
            "feature_version",
            "dataset_version",
            name="uq_feature_snapshot_customer_version",
        ),
    )
    op.create_index(
        op.f("ix_feature_snapshots_customer_id"),
        "feature_snapshots",
        ["customer_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_feature_snapshots_customer_id"), table_name="feature_snapshots"
    )
    op.drop_table("feature_snapshots")
    op.drop_index(op.f("ix_transactions_customer_id"), table_name="transactions")
    op.drop_table("transactions")
    op.drop_index(op.f("ix_products_customer_id"), table_name="products")
    op.drop_table("products")
    op.drop_index(op.f("ix_loans_customer_id"), table_name="loans")
    op.drop_table("loans")
    op.drop_index(op.f("ix_ingestion_runs_dataset_name"), table_name="ingestion_runs")
    op.drop_table("ingestion_runs")
    op.drop_table("dataset_metadata")
    op.drop_table("customers")
