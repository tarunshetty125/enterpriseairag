from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.settings import to_camel


class DatasetMetadataResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    dataset_name: str
    source: str
    version: str
    rows: int
    columns: list[str]
    imported_at: datetime
    checksum: str
    status: str


class IngestionRunResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    dataset_name: str
    started_at: datetime
    finished_at: datetime | None
    status: str
    rows_processed: int
    message: str | None


class IngestionSummaryResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    dataset_name: str
    status: str
    rows_processed: int
    checksum: str
    started_at: datetime
    finished_at: datetime
    message: str


class IngestionResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    status: str
    datasets: list[IngestionSummaryResponse]
    feature_snapshots_generated: int
    quality_score: float


class DatasetStatusResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    configured_datasets: int
    loaded_datasets: int
    rows_loaded: int
    sqlite_path: str
    sqlite_size_bytes: int
    latest_ingestion: IngestionRunResponse | None
    table_counts: dict[str, int]
    quality_score: float
    feature_store: dict[str, Any]
