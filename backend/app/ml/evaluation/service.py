from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.ml.registry.service import ModelRegistryService


class MLEvaluationService:
    """Reads active model evaluation metrics from the registry."""

    def __init__(self, session: Session) -> None:
        self.registry = ModelRegistryService(session)
        self.settings = get_settings().ml

    def summary(self) -> dict[str, Any | None]:
        risk = self.registry.active_model(self.settings.risk_model_name)
        segmentation = self.registry.active_model(self.settings.segmentation_model_name)
        return {
            "risk": risk.metrics if risk is not None else None,
            "segmentation": segmentation.metrics if segmentation is not None else None,
        }
