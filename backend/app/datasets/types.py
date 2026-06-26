from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

RawRow = dict[str, str]
NormalizedRow = dict[str, str]


@dataclass(frozen=True)
class ValidationIssue:
    column: str
    message: str


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    missing_columns: list[str] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)


@dataclass(frozen=True)
class CanonicalCustomerRecord:
    customer_id: str
    full_name: str | None
    gender: str | None
    age: int | None
    geography: str | None
    education: str | None
    marital_status: str | None
    income_category: str | None
    estimated_income: float | None
    credit_score: int | None
    savings_balance: float | None
    tenure_months: int | None
    source_dataset: str
    source_record_id: str
    external_references: dict[str, Any]


@dataclass(frozen=True)
class CanonicalLoanRecord:
    customer_id: str
    loan_type: str
    amount: float
    term_months: int | None
    status: str
    credit_history: float | None
    property_area: str | None
    source_dataset: str
    source_record_id: str


@dataclass(frozen=True)
class CanonicalTransactionRecord:
    customer_id: str
    step: int | None
    transaction_type: str
    category: str
    direction: str
    amount: float
    description: str
    counterparty: str | None
    is_fraud: int
    source_dataset: str
    source_record_id: str


@dataclass(frozen=True)
class CanonicalProductRecord:
    customer_id: str
    product_type: str
    status: str
    credit_limit: float | None
    revolving_balance: float | None
    revenue: float
    source_dataset: str
    source_record_id: str


@dataclass(frozen=True)
class CanonicalBatch:
    customers: list[CanonicalCustomerRecord] = field(default_factory=list)
    loans: list[CanonicalLoanRecord] = field(default_factory=list)
    transactions: list[CanonicalTransactionRecord] = field(default_factory=list)
    products: list[CanonicalProductRecord] = field(default_factory=list)


@dataclass(frozen=True)
class IngestionSummary:
    dataset_name: str
    status: str
    rows_processed: int
    checksum: str
    started_at: datetime
    finished_at: datetime
    message: str


@dataclass(frozen=True)
class QualityCheck:
    name: str
    status: str
    affected_rows: int
    details: str


@dataclass(frozen=True)
class QualityReport:
    score: float
    checks: list[QualityCheck]
