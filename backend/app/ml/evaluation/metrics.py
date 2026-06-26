from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    davies_bouldin_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    silhouette_score,
)

from app.ml.utils.constants import RISK_LABELS


def evaluate_classification(
    y_true: list[str],
    y_pred: list[str],
    probabilities: np.ndarray | None,
    labels: list[str] | None = None,
) -> dict[str, Any]:
    ordered_labels = labels or list(RISK_LABELS)
    metrics: dict[str, Any] = {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(
            float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
            4,
        ),
        "recall": round(
            float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
            4,
        ),
        "f1": round(
            float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
            4,
        ),
        "classification_report": classification_report(
            y_true,
            y_pred,
            labels=ordered_labels,
            output_dict=True,
            zero_division=0,
        ),
        "confusion_matrix": confusion_matrix(
            y_true,
            y_pred,
            labels=ordered_labels,
        ).tolist(),
        "labels": ordered_labels,
    }
    metrics["roc_auc"] = _safe_roc_auc(y_true, probabilities, ordered_labels)
    return metrics


def evaluate_segmentation(
    scaled_matrix: np.ndarray,
    labels: np.ndarray,
    inertia: float,
    distribution: dict[str, int],
) -> dict[str, Any]:
    metrics: dict[str, Any] = {
        "inertia": round(float(inertia), 4),
        "customer_count": int(len(labels)),
        "distribution": distribution,
    }
    unique_labels = set(int(label) for label in labels.tolist())
    if len(unique_labels) > 1 and len(labels) > len(unique_labels):
        metrics["silhouette_score"] = round(
            float(silhouette_score(scaled_matrix, labels)),
            4,
        )
        metrics["davies_bouldin_score"] = round(
            float(davies_bouldin_score(scaled_matrix, labels)),
            4,
        )
    else:
        metrics["silhouette_score"] = None
        metrics["davies_bouldin_score"] = None
    return metrics


def _safe_roc_auc(
    y_true: list[str],
    probabilities: np.ndarray | None,
    labels: list[str],
) -> float | None:
    if probabilities is None or len(set(y_true)) < 2:
        return None
    try:
        score = roc_auc_score(
            y_true,
            probabilities,
            labels=labels,
            multi_class="ovr",
            average="weighted",
        )
    except ValueError:
        return None
    return round(float(score), 4)
