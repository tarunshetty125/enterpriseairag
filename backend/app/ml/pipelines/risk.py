from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from time import perf_counter
from typing import Any

from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.ml.evaluation.metrics import evaluate_classification
from app.ml.models.artifact_store import ModelArtifactStore
from app.ml.preprocessing.feature_matrix import FeatureMatrixBuilder
from app.ml.registry.service import ModelRegistration, ModelRegistryService
from app.ml.utils.constants import ML_FEATURE_COLUMNS, RISK_LABELS
from app.models.ml import MLModelRegistry


class RiskPipeline:
    """Reusable supervised training pipeline for customer risk prediction."""

    def __init__(
        self,
        session: Session,
        artifact_store: ModelArtifactStore | None = None,
    ) -> None:
        self.session = session
        self.settings = get_settings().ml
        self.artifact_store = artifact_store or ModelArtifactStore()

    def train(self) -> MLModelRegistry:
        training_matrix = FeatureMatrixBuilder(
            self.session
        ).build_risk_training_matrix()
        target_counts = Counter(training_matrix.target.tolist())
        if len(target_counts) < 2:
            msg = "Risk training requires at least two risk classes."
            raise ValueError(msg)

        stratify = training_matrix.target if min(target_counts.values()) >= 2 else None
        started = perf_counter()
        x_train, x_test, y_train, y_test = train_test_split(
            training_matrix.frame,
            training_matrix.target,
            test_size=self.settings.test_size,
            random_state=self.settings.random_seed,
            stratify=stratify,
        )
        pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    RandomForestClassifier(
                        n_estimators=120,
                        max_depth=9,
                        min_samples_leaf=4,
                        class_weight="balanced",
                        random_state=self.settings.random_seed,
                        n_jobs=1,
                    ),
                ),
            ]
        )
        pipeline.fit(x_train, y_train)
        predictions = list(pipeline.predict(x_test))
        classifier = pipeline.named_steps["classifier"]
        probabilities = (
            pipeline.predict_proba(x_test)
            if hasattr(classifier, "predict_proba")
            else None
        )
        metrics = evaluate_classification(
            list(y_test),
            predictions,
            probabilities,
            labels=list(classifier.classes_),
        )
        training_time_ms = round((perf_counter() - started) * 1000, 2)
        feature_importance = self._feature_importance(classifier.feature_importances_)
        metrics["feature_importance"] = feature_importance

        version = self._version()
        payload = {
            "model_name": self.settings.risk_model_name,
            "version": version,
            "model_type": "risk_prediction",
            "algorithm": "RandomForestClassifier",
            "pipeline": pipeline,
            "features": list(ML_FEATURE_COLUMNS),
            "labels": list(RISK_LABELS),
            "trained_at": datetime.now(UTC).isoformat(),
            "metrics": metrics,
            "feature_descriptions": training_matrix.feature_descriptions,
        }
        artifact_path = self.artifact_store.save(
            self.settings.risk_model_name,
            version,
            payload,
        )
        return ModelRegistryService(self.session).register(
            ModelRegistration(
                model_name=self.settings.risk_model_name,
                version=version,
                algorithm="RandomForestClassifier",
                metrics=metrics,
                accuracy=self._metric(metrics, "accuracy"),
                precision=self._metric(metrics, "precision"),
                recall=self._metric(metrics, "recall"),
                f1=self._metric(metrics, "f1"),
                features_used=list(ML_FEATURE_COLUMNS),
                artifact_path=artifact_path.as_posix(),
                dataset_version=training_matrix.dataset_version,
                feature_version=training_matrix.feature_version,
                training_time_ms=training_time_ms,
                training_metadata={
                    "target_distribution": dict(target_counts),
                    "train_rows": len(x_train),
                    "test_rows": len(x_test),
                    "test_size": self.settings.test_size,
                    "random_seed": self.settings.random_seed,
                },
            )
        )

    def _feature_importance(self, importances: Any) -> list[dict[str, float | str]]:
        rows: list[dict[str, float | str]] = [
            {
                "name": feature,
                "importance": round(float(importance), 6),
            }
            for feature, importance in zip(
                ML_FEATURE_COLUMNS,
                importances,
                strict=True,
            )
        ]
        return sorted(rows, key=lambda item: float(item["importance"]), reverse=True)

    def _version(self) -> str:
        return datetime.now(UTC).strftime("risk_%Y%m%d%H%M%S")

    def _metric(self, metrics: dict[str, Any], key: str) -> float | None:
        value = metrics.get(key)
        if isinstance(value, int | float):
            return float(value)
        return None
