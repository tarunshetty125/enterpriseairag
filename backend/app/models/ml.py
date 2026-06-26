from __future__ import annotations

from datetime import datetime
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
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.canonical import utc_now


class MLModelRegistry(Base):
    __tablename__ = "ml_model_registry"
    __table_args__ = (
        UniqueConstraint("model_name", "version", name="uq_ml_model_name_version"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(80), nullable=False)
    algorithm: Mapped[str] = mapped_column(String(120), nullable=False)
    training_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    metrics: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    precision: Mapped[float | None] = mapped_column(Float, nullable=True)
    recall: Mapped[float | None] = mapped_column(Float, nullable=True)
    f1: Mapped[float | None] = mapped_column(Float, nullable=True)
    features_used: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    artifact_path: Mapped[str] = mapped_column(Text, nullable=False)
    dataset_version: Mapped[str] = mapped_column(String(80), nullable=False)
    feature_version: Mapped[str] = mapped_column(String(40), nullable=False)
    active_model: Mapped[int] = mapped_column(Integer, default=0, index=True)
    training_time_ms: Mapped[float] = mapped_column(Float, default=0.0)
    inference_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    training_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class MLPredictionLog(Base):
    __tablename__ = "ml_prediction_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_id: Mapped[int] = mapped_column(
        ForeignKey("ml_model_registry.id"), nullable=False, index=True
    )
    model_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    model_version: Mapped[str] = mapped_column(String(80), nullable=False)
    customer_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    prediction: Mapped[str] = mapped_column(String(80), nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    inference_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
