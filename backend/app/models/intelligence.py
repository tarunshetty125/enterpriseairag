from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.canonical import utc_now


class TransactionInsight(Base):
    __tablename__ = "transaction_insights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transactions.id"), nullable=False, unique=True, index=True
    )
    customer_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    raw_description: Mapped[str] = mapped_column(String(240), nullable=False)
    cleaned_description: Mapped[str] = mapped_column(String(240), nullable=False)
    normalized_description: Mapped[str] = mapped_column(String(240), nullable=False)
    keywords: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    entities: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    sentiment_label: Mapped[str] = mapped_column(String(40), nullable=False)
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=False)
    lifestyle_indicators: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    processing_version: Mapped[str] = mapped_column(String(40), nullable=False)
    processing_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )


class BehaviourProfile(Base):
    __tablename__ = "behaviour_profiles"

    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customers.customer_id"), primary_key=True
    )
    profile_version: Mapped[str] = mapped_column(String(40), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    flags: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    lifestyle_indicators: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    category_spend: Mapped[dict[str, float]] = mapped_column(JSON, nullable=False)
    category_counts: Mapped[dict[str, int]] = mapped_column(JSON, nullable=False)
    monthly_trends: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    top_merchants: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    features: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    processing_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )


class RecommendationRule(Base):
    __tablename__ = "recommendation_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_id: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    product_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    conditions: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    base_score: Mapped[float] = mapped_column(Float, nullable=False)
    version: Mapped[str] = mapped_column(String(40), nullable=False)
    active: Mapped[int] = mapped_column(Integer, default=1, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    rule_id: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    product_name: Mapped[str] = mapped_column(String(120), nullable=False)
    suitability_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    supporting_features: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, nullable=False
    )
    business_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation_version: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="active", index=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )


class RecommendationHistory(Base):
    __tablename__ = "recommendation_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    recommendation_id: Mapped[int | None] = mapped_column(
        ForeignKey("recommendations.id"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
