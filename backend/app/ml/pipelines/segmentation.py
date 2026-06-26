from __future__ import annotations

from datetime import UTC, datetime
from time import perf_counter
from typing import Any

import numpy as np
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.ml.evaluation.metrics import evaluate_segmentation
from app.ml.models.artifact_store import ModelArtifactStore
from app.ml.preprocessing.feature_matrix import FeatureMatrixBuilder
from app.ml.registry.service import ModelRegistration, ModelRegistryService
from app.ml.utils.constants import ML_FEATURE_COLUMNS
from app.models.ml import MLModelRegistry


class SegmentationPipeline:
    """Reusable KMeans training pipeline for customer segmentation."""

    def __init__(
        self,
        session: Session,
        artifact_store: ModelArtifactStore | None = None,
    ) -> None:
        self.session = session
        self.settings = get_settings().ml
        self.artifact_store = artifact_store or ModelArtifactStore()

    def train(self) -> MLModelRegistry:
        matrix = FeatureMatrixBuilder(self.session).build_segmentation_matrix()
        if len(matrix.frame) < 2:
            msg = "Segmentation training requires at least two customers."
            raise ValueError(msg)
        cluster_count = min(self.settings.segmentation_clusters, len(matrix.frame))
        started = perf_counter()
        pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                (
                    "clusterer",
                    KMeans(
                        n_clusters=cluster_count,
                        n_init=10,
                        random_state=self.settings.random_seed,
                    ),
                ),
            ]
        )
        cluster_ids = np.asarray(pipeline.fit_predict(matrix.frame))
        scaled_matrix = self._scaled_matrix(pipeline, matrix.frame)
        centroid_by_cluster = self._centroid_summary(matrix.frame, cluster_ids)
        label_mapping = self._assign_business_labels(centroid_by_cluster)
        distribution = self._distribution(cluster_ids, label_mapping)
        centroid_by_label = {
            label_mapping[cluster_id]: centroid
            for cluster_id, centroid in centroid_by_cluster.items()
        }
        clusterer = pipeline.named_steps["clusterer"]
        metrics = evaluate_segmentation(
            scaled_matrix,
            cluster_ids,
            float(clusterer.inertia_),
            distribution,
        )
        metrics["centroid_summary"] = centroid_by_label
        metrics["business_labels"] = list(distribution.keys())
        training_time_ms = round((perf_counter() - started) * 1000, 2)

        version = self._version()
        payload = {
            "model_name": self.settings.segmentation_model_name,
            "version": version,
            "model_type": "customer_segmentation",
            "algorithm": "KMeans",
            "pipeline": pipeline,
            "features": list(ML_FEATURE_COLUMNS),
            "label_mapping": label_mapping,
            "centroid_summary": centroid_by_label,
            "distribution": distribution,
            "trained_at": datetime.now(UTC).isoformat(),
            "metrics": metrics,
            "feature_descriptions": matrix.feature_descriptions,
        }
        artifact_path = self.artifact_store.save(
            self.settings.segmentation_model_name,
            version,
            payload,
        )
        return ModelRegistryService(self.session).register(
            ModelRegistration(
                model_name=self.settings.segmentation_model_name,
                version=version,
                algorithm="KMeans",
                metrics=metrics,
                accuracy=None,
                precision=None,
                recall=None,
                f1=None,
                features_used=list(ML_FEATURE_COLUMNS),
                artifact_path=artifact_path.as_posix(),
                dataset_version=matrix.dataset_version,
                feature_version=matrix.feature_version,
                training_time_ms=training_time_ms,
                training_metadata={
                    "cluster_count": cluster_count,
                    "customer_count": len(matrix.frame),
                    "random_seed": self.settings.random_seed,
                },
            )
        )

    def _scaled_matrix(self, pipeline: Pipeline, frame: Any) -> Any:
        imputed = pipeline.named_steps["imputer"].transform(frame)
        return pipeline.named_steps["scaler"].transform(imputed)

    def _centroid_summary(
        self,
        frame: Any,
        cluster_ids: np.ndarray,
    ) -> dict[int, dict[str, float]]:
        enriched = frame.copy()
        enriched["cluster_id"] = cluster_ids
        summary: dict[int, dict[str, float]] = {}
        for cluster_id, group in enriched.groupby("cluster_id"):
            values = group.drop(columns=["cluster_id"]).mean(numeric_only=True)
            summary[int(cluster_id)] = {
                str(feature): round(float(values[feature]), 4)
                for feature in ML_FEATURE_COLUMNS
            }
        return summary

    def _assign_business_labels(
        self,
        centroids: dict[int, dict[str, float]],
    ) -> dict[int, str]:
        remaining = set(centroids)
        assignments: dict[int, str] = {}

        def assign(label: str, scorer: Any, *, reverse: bool = True) -> None:
            if not remaining:
                return
            cluster_id = sorted(
                remaining,
                key=lambda item: scorer(centroids[item]),
                reverse=reverse,
            )[0]
            assignments[cluster_id] = label
            remaining.remove(cluster_id)

        assign(
            "Loan Focused",
            lambda row: row["debt_to_income"]
            + row["risk_indicators"]
            + (row["loan_exposure"] / 100000),
        )
        assign(
            "Premium",
            lambda row: (row["estimated_income"] / 100000)
            + row["savings_ratio"]
            + (row["credit_score"] / 850),
        )
        assign("Young Investors", lambda row: row["age"], reverse=False)
        assign(
            "Budget",
            lambda row: (row["estimated_income"] / 100000)
            + row["savings_ratio"]
            + row["product_count"],
            reverse=False,
        )
        assign(
            "High Value",
            lambda row: row["product_count"] + (row["estimated_income"] / 100000),
        )
        return assignments

    def _distribution(
        self,
        cluster_ids: np.ndarray,
        label_mapping: dict[int, str],
    ) -> dict[str, int]:
        distribution: dict[str, int] = {}
        for cluster_id in cluster_ids:
            label = label_mapping[int(cluster_id)]
            distribution[label] = distribution.get(label, 0) + 1
        return dict(sorted(distribution.items()))

    def _version(self) -> str:
        return datetime.now(UTC).strftime("segment_%Y%m%d%H%M%S")
