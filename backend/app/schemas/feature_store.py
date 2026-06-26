from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.settings import to_camel


class FeatureStoreStatusResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    feature_version: str
    dataset_version: str
    snapshot_count: int
    customer_count: int
    latest_generated_at: datetime | None
    feature_count: int
    coverage: float
