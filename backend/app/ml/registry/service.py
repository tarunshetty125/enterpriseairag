from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ml import MLModelRegistry, MLPredictionLog


@dataclass(frozen=True)
class ModelRegistration:
    model_name: str
    version: str
    algorithm: str
    metrics: dict[str, Any]
    accuracy: float | None
    precision: float | None
    recall: float | None
    f1: float | None
    features_used: list[str]
    artifact_path: str
    dataset_version: str
    feature_version: str
    training_time_ms: float
    training_metadata: dict[str, Any]


class ModelRegistryService:
    """Persists model metadata and active model state."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def register(self, registration: ModelRegistration) -> MLModelRegistry:
        self._deactivate_model_name(registration.model_name)
        existing = self.session.scalar(
            select(MLModelRegistry).where(
                MLModelRegistry.model_name == registration.model_name,
                MLModelRegistry.version == registration.version,
            )
        )
        if existing is not None:
            msg = (
                f"Model {registration.model_name} version "
                f"{registration.version} is already registered"
            )
            raise ValueError(msg)

        model = MLModelRegistry(
            model_name=registration.model_name,
            version=registration.version,
            algorithm=registration.algorithm,
            training_date=datetime.now(UTC),
            metrics=registration.metrics,
            accuracy=registration.accuracy,
            precision=registration.precision,
            recall=registration.recall,
            f1=registration.f1,
            features_used=registration.features_used,
            artifact_path=registration.artifact_path,
            dataset_version=registration.dataset_version,
            feature_version=registration.feature_version,
            active_model=1,
            training_time_ms=registration.training_time_ms,
            inference_time_ms=None,
            training_metadata=registration.training_metadata,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return model

    def list_models(self) -> list[MLModelRegistry]:
        return list(
            self.session.scalars(
                select(MLModelRegistry).order_by(
                    MLModelRegistry.training_date.desc(),
                    MLModelRegistry.model_name,
                )
            )
        )

    def get_model(self, model: str) -> MLModelRegistry | None:
        exact_id = self._parse_int(model)
        if exact_id is not None:
            return self.session.get(MLModelRegistry, exact_id)
        active = self.active_model(model)
        if active is not None:
            return active
        return self.session.scalar(
            select(MLModelRegistry)
            .where(MLModelRegistry.model_name == model)
            .order_by(MLModelRegistry.training_date.desc())
            .limit(1)
        )

    def active_model(self, model_name: str) -> MLModelRegistry | None:
        return self.session.scalar(
            select(MLModelRegistry)
            .where(
                MLModelRegistry.model_name == model_name,
                MLModelRegistry.active_model == 1,
            )
            .order_by(MLModelRegistry.training_date.desc())
            .limit(1)
        )

    def activate(self, model_id: int) -> MLModelRegistry | None:
        model = self.session.get(MLModelRegistry, model_id)
        if model is None:
            return None
        self._deactivate_model_name(model.model_name)
        model.active_model = 1
        self.session.commit()
        self.session.refresh(model)
        return model

    def record_prediction(
        self,
        *,
        model: MLModelRegistry,
        customer_id: str,
        prediction: str,
        confidence: float | None,
        inference_time_ms: float,
    ) -> None:
        model.inference_time_ms = inference_time_ms
        self.session.add(
            MLPredictionLog(
                model_id=model.id,
                model_name=model.model_name,
                model_version=model.version,
                customer_id=customer_id,
                prediction=prediction,
                confidence=confidence,
                inference_time_ms=inference_time_ms,
            )
        )
        self.session.commit()

    def prediction_count(self, model_id: int | None = None) -> int:
        statement = select(func.count(MLPredictionLog.id))
        if model_id is not None:
            statement = statement.where(MLPredictionLog.model_id == model_id)
        return self.session.scalar(statement) or 0

    def latest_training(self) -> MLModelRegistry | None:
        return self.session.scalar(
            select(MLModelRegistry)
            .order_by(MLModelRegistry.training_date.desc())
            .limit(1)
        )

    def _deactivate_model_name(self, model_name: str) -> None:
        for model in self.session.scalars(
            select(MLModelRegistry).where(MLModelRegistry.model_name == model_name)
        ):
            model.active_model = 0

    def _parse_int(self, value: str) -> int | None:
        try:
            return int(value)
        except ValueError:
            return None
