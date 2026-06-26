from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any

import numpy as np
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.ml.models.artifact_store import ModelArtifactStore
from app.ml.prediction.explainability import (
    ExplainabilityEngine,
    FeatureContribution,
)
from app.ml.preprocessing.feature_matrix import FeatureMatrixBuilder
from app.ml.registry.service import ModelRegistryService
from app.models.ml import MLModelRegistry


@dataclass(frozen=True)
class RiskPredictionResult:
    customer_id: str
    risk_level: str
    confidence: float
    probabilities: dict[str, float]
    top_features: list[FeatureContribution]
    business_explanation: str
    model_version: str
    inference_time_ms: float


@dataclass(frozen=True)
class SegmentPredictionResult:
    customer_id: str
    segment_label: str
    confidence: float
    nearest_distance: float
    centroid_summary: dict[str, float]
    model_version: str
    inference_time_ms: float


class PredictionPipeline:
    """Loads active ML artifacts and produces real customer predictions."""

    def __init__(
        self,
        session: Session,
        artifact_store: ModelArtifactStore | None = None,
    ) -> None:
        self.session = session
        self.settings = get_settings().ml
        self.artifact_store = artifact_store or ModelArtifactStore()
        self.registry = ModelRegistryService(session)
        self.features = FeatureMatrixBuilder(session)
        self.explainability = ExplainabilityEngine()

    def predict_risk(self, customer_id: str) -> RiskPredictionResult:
        model = self._active_model(self.settings.risk_model_name)
        payload = self.artifact_store.load(model.artifact_path)
        vector = self.features.build_customer_vector(customer_id)
        pipeline = payload["pipeline"]

        started = perf_counter()
        prediction = str(pipeline.predict(vector.frame)[0])
        probabilities = self._risk_probabilities(pipeline, vector.frame)
        confidence = round(max(probabilities.values()) if probabilities else 0.0, 4)
        inference_time_ms = round((perf_counter() - started) * 1000, 2)
        top_features = self._top_features(payload, vector.raw_features, limit=5)
        explanation = self.explainability.summarize(
            prediction=prediction,
            contributions=top_features,
        )
        self.registry.record_prediction(
            model=model,
            customer_id=customer_id,
            prediction=prediction,
            confidence=confidence,
            inference_time_ms=inference_time_ms,
        )
        return RiskPredictionResult(
            customer_id=customer_id,
            risk_level=prediction,
            confidence=confidence,
            probabilities=probabilities,
            top_features=top_features,
            business_explanation=explanation,
            model_version=model.version,
            inference_time_ms=inference_time_ms,
        )

    def predict_segment(self, customer_id: str) -> SegmentPredictionResult:
        model = self._active_model(self.settings.segmentation_model_name)
        payload = self.artifact_store.load(model.artifact_path)
        vector = self.features.build_customer_vector(customer_id)
        pipeline = payload["pipeline"]

        started = perf_counter()
        cluster_id = int(pipeline.predict(vector.frame)[0])
        distances = np.asarray(pipeline.transform(vector.frame)[0])
        nearest_distance = round(float(distances[cluster_id]), 4)
        confidence = self._distance_confidence(distances, cluster_id)
        inference_time_ms = round((perf_counter() - started) * 1000, 2)
        label_mapping = self._label_mapping(payload.get("label_mapping"))
        label = label_mapping[cluster_id]
        centroid_summary = self._centroid_summary(payload, label)
        self.registry.record_prediction(
            model=model,
            customer_id=customer_id,
            prediction=label,
            confidence=confidence,
            inference_time_ms=inference_time_ms,
        )
        return SegmentPredictionResult(
            customer_id=customer_id,
            segment_label=label,
            confidence=confidence,
            nearest_distance=nearest_distance,
            centroid_summary=centroid_summary,
            model_version=model.version,
            inference_time_ms=inference_time_ms,
        )

    def feature_importance(
        self,
        limit: int = 10,
    ) -> tuple[MLModelRegistry, list[FeatureContribution]]:
        model = self._active_model(self.settings.risk_model_name)
        payload = self.artifact_store.load(model.artifact_path)
        contributions = self._top_features(payload, {}, limit=limit)
        return model, contributions

    def _active_model(self, model_name: str) -> MLModelRegistry:
        model = self.registry.active_model(model_name)
        if model is None:
            msg = f"No active model registered for {model_name}."
            raise ValueError(msg)
        return model

    def _risk_probabilities(self, pipeline: Any, frame: Any) -> dict[str, float]:
        probabilities = pipeline.predict_proba(frame)[0]
        classifier = pipeline.named_steps["classifier"]
        return {
            str(label): round(float(probability), 4)
            for label, probability in zip(
                classifier.classes_,
                probabilities,
                strict=True,
            )
        }

    def _top_features(
        self,
        payload: dict[str, Any],
        raw_features: dict[str, float],
        *,
        limit: int,
    ) -> list[FeatureContribution]:
        metrics = self._dict_value(payload.get("metrics"))
        descriptions = self._dict_value(payload.get("feature_descriptions"))
        importance_rows = self._list_value(metrics.get("feature_importance"))
        contributions: list[FeatureContribution] = []
        for row in importance_rows[:limit]:
            row_dict = self._dict_value(row)
            name = str(row_dict.get("name", "unknown"))
            importance = float(row_dict.get("importance", 0.0))
            contributions.append(
                FeatureContribution(
                    name=name,
                    value=raw_features.get(name),
                    importance=importance,
                    description=str(descriptions.get(name, "")),
                )
            )
        return contributions

    def _distance_confidence(self, distances: np.ndarray, cluster_id: int) -> float:
        inverse = 1 / np.maximum(distances, 1e-9)
        confidence = float(inverse[cluster_id] / inverse.sum())
        return round(confidence, 4)

    def _label_mapping(self, value: Any) -> dict[int, str]:
        mapping = self._dict_value(value)
        return {int(key): str(label) for key, label in mapping.items()}

    def _centroid_summary(
        self,
        payload: dict[str, Any],
        label: str,
    ) -> dict[str, float]:
        summary = self._dict_value(payload.get("centroid_summary"))
        row = self._dict_value(summary.get(label))
        return {
            str(feature): round(float(value), 4)
            for feature, value in row.items()
            if isinstance(value, int | float)
        }

    def _dict_value(self, value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return value
        return {}

    def _list_value(self, value: Any) -> list[Any]:
        if isinstance(value, list):
            return value
        return []
