from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.settings import to_camel


class ModelRegistryItemResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    model_name: str
    version: str
    algorithm: str
    training_date: datetime
    metrics: dict[str, Any]
    accuracy: float | None
    precision: float | None
    recall: float | None
    f1: float | None
    features_used: list[str]
    artifact_path: str
    dataset_version: str
    feature_version: str
    active_model: bool
    training_time_ms: float
    inference_time_ms: float | None
    training_metadata: dict[str, Any]
    prediction_count: int


class ModelRegistryListResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    models: list[ModelRegistryItemResponse]


class TrainModelResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    model: ModelRegistryItemResponse
    message: str


class RiskPredictionRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    customer_id: str


class SegmentPredictionRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    customer_id: str


class FeatureContributionResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str
    value: float | str | None
    importance: float
    description: str


class RiskPredictionResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    customer_id: str
    risk_level: str
    confidence: float
    probabilities: dict[str, float]
    top_features: list[FeatureContributionResponse]
    business_explanation: str
    model_version: str
    inference_time_ms: float


class SegmentPredictionResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    customer_id: str
    segment_label: str
    confidence: float
    nearest_distance: float
    centroid_summary: dict[str, float]
    model_version: str
    inference_time_ms: float


class EvaluationResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    risk: dict[str, Any] | None
    segmentation: dict[str, Any] | None


class FeatureImportanceResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    model_name: str
    model_version: str
    features: list[FeatureContributionResponse]
