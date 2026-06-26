from __future__ import annotations

from sqlalchemy.orm import Session

from app.ml.pipelines.risk import RiskPipeline
from app.ml.pipelines.segmentation import SegmentationPipeline
from app.models.ml import MLModelRegistry


class MLTrainingService:
    """Explicit training entry point for Phase 3 models."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def train_risk_model(self) -> MLModelRegistry:
        return RiskPipeline(self.session).train()

    def train_segmentation_model(self) -> MLModelRegistry:
        return SegmentationPipeline(self.session).train()
