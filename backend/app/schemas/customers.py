from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.settings import to_camel


class LoanResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    loan_type: str
    amount: float
    term_months: int | None
    status: str
    credit_history: float | None
    property_area: str | None


class TransactionResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    step: int | None
    transaction_type: str
    category: str
    direction: str
    amount: float
    description: str
    counterparty: str | None
    is_fraud: int


class ProductResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    product_type: str
    status: str
    credit_limit: float | None
    revolving_balance: float | None
    revenue: float


class CustomerListItemResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    customer_id: str
    full_name: str | None
    gender: str | None
    age: int | None
    geography: str | None
    income_category: str | None
    estimated_income: float | None
    credit_score: int | None
    source_dataset: str


class CustomerListResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    total: int
    items: list[CustomerListItemResponse]


class FeatureItemResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str
    value: Any
    description: str
    version: str
    dataset_version: str
    generated_at: datetime


class CustomerFeaturesResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    customer_id: str
    features: list[FeatureItemResponse]


class CustomerDetailResponse(CustomerListItemResponse):
    education: str | None
    marital_status: str | None
    savings_balance: float | None
    tenure_months: int | None
    external_references: dict[str, Any]
    loans: list[LoanResponse]
    transactions: list[TransactionResponse]
    products: list[ProductResponse]
    features: list[FeatureItemResponse]
