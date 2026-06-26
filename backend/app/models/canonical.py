from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    full_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(32), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    geography: Mapped[str | None] = mapped_column(String(80), nullable=True)
    education: Mapped[str | None] = mapped_column(String(80), nullable=True)
    marital_status: Mapped[str | None] = mapped_column(String(80), nullable=True)
    income_category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    estimated_income: Mapped[float | None] = mapped_column(Float, nullable=True)
    credit_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    savings_balance: Mapped[float | None] = mapped_column(Float, nullable=True)
    tenure_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_dataset: Mapped[str] = mapped_column(String(120), nullable=False)
    source_record_id: Mapped[str] = mapped_column(String(160), nullable=False)
    external_references: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    loans: Mapped[list[Loan]] = relationship(back_populates="customer")
    transactions: Mapped[list[Transaction]] = relationship(back_populates="customer")
    products: Mapped[list[Product]] = relationship(back_populates="customer")
    feature_snapshots: Mapped[list[FeatureSnapshot]] = relationship(
        back_populates="customer"
    )


class Loan(Base):
    __tablename__ = "loans"
    __table_args__ = (
        UniqueConstraint(
            "source_dataset", "source_record_id", name="uq_loans_source_record"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customers.customer_id"), index=True
    )
    loan_type: Mapped[str] = mapped_column(String(80), default="Personal Loan")
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    term_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="unknown")
    credit_history: Mapped[float | None] = mapped_column(Float, nullable=True)
    property_area: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source_dataset: Mapped[str] = mapped_column(String(120), nullable=False)
    source_record_id: Mapped[str] = mapped_column(String(160), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    customer: Mapped[Customer] = relationship(back_populates="loans")


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        UniqueConstraint(
            "source_dataset",
            "source_record_id",
            name="uq_transactions_source_record",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customers.customer_id"), index=True
    )
    step: Mapped[int | None] = mapped_column(Integer, nullable=True)
    transaction_type: Mapped[str] = mapped_column(String(80), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(String(240), nullable=False)
    counterparty: Mapped[str | None] = mapped_column(String(160), nullable=True)
    is_fraud: Mapped[int] = mapped_column(Integer, default=0)
    source_dataset: Mapped[str] = mapped_column(String(120), nullable=False)
    source_record_id: Mapped[str] = mapped_column(String(160), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    customer: Mapped[Customer] = relationship(back_populates="transactions")


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint(
            "source_dataset", "source_record_id", name="uq_products_source_record"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customers.customer_id"), index=True
    )
    product_type: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="active")
    credit_limit: Mapped[float | None] = mapped_column(Float, nullable=True)
    revolving_balance: Mapped[float | None] = mapped_column(Float, nullable=True)
    revenue: Mapped[float] = mapped_column(Float, default=0.0)
    source_dataset: Mapped[str] = mapped_column(String(120), nullable=False)
    source_record_id: Mapped[str] = mapped_column(String(160), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    customer: Mapped[Customer] = relationship(back_populates="products")


class FeatureSnapshot(Base):
    __tablename__ = "feature_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "customer_id",
            "feature_version",
            "dataset_version",
            name="uq_feature_snapshot_customer_version",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customers.customer_id"), index=True
    )
    feature_version: Mapped[str] = mapped_column(String(40), nullable=False)
    dataset_version: Mapped[str] = mapped_column(String(80), nullable=False)
    features: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    customer: Mapped[Customer] = relationship(back_populates="feature_snapshots")


class DatasetMetadata(Base):
    __tablename__ = "dataset_metadata"

    dataset_name: Mapped[str] = mapped_column(String(120), primary_key=True)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(String(80), nullable=False)
    rows: Mapped[int] = mapped_column(Integer, nullable=False)
    columns: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    checksum: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    rows_processed: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
