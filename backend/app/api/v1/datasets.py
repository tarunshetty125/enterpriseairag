from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.serializers import serialize_dataset_metadata, serialize_ingestion_run
from app.datasets.quality import DataQualityService
from app.datasets.service import DatasetService, SeedService
from app.db.session import get_db_session
from app.feature_store.service import FeatureStoreService
from app.schemas.datasets import (
    DatasetMetadataResponse,
    DatasetStatusResponse,
    IngestionResponse,
    IngestionSummaryResponse,
)

router = APIRouter(prefix="/datasets", tags=["datasets"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("", response_model=list[DatasetMetadataResponse])
def list_datasets(
    session: DbSession,
) -> list[DatasetMetadataResponse]:
    return [
        serialize_dataset_metadata(item)
        for item in DatasetService(session).list_datasets()
    ]


@router.post("/ingest", response_model=IngestionResponse)
def ingest_datasets(session: DbSession) -> IngestionResponse:
    result = SeedService(session).ingest_all()
    return IngestionResponse(
        status="completed",
        datasets=[
            IngestionSummaryResponse(
                dataset_name=summary.dataset_name,
                status=summary.status,
                rows_processed=summary.rows_processed,
                checksum=summary.checksum,
                started_at=summary.started_at,
                finished_at=summary.finished_at,
                message=summary.message,
            )
            for summary in result.summaries
        ],
        feature_snapshots_generated=result.feature_snapshots_generated,
        quality_score=result.quality_report.score,
    )


@router.get("/status", response_model=DatasetStatusResponse)
def dataset_status(session: DbSession) -> DatasetStatusResponse:
    dataset_service = DatasetService(session)
    status = dataset_service.status()
    quality_report = DataQualityService(session).report()
    feature_store_status = FeatureStoreService(session).status()
    return DatasetStatusResponse(
        configured_datasets=status["configured_datasets"],
        loaded_datasets=status["loaded_datasets"],
        rows_loaded=status["rows_loaded"],
        sqlite_path=status["sqlite_path"],
        sqlite_size_bytes=status["sqlite_size_bytes"],
        latest_ingestion=serialize_ingestion_run(status["latest_ingestion"]),
        table_counts=dataset_service.table_counts(),
        quality_score=quality_report.score,
        feature_store=feature_store_status,
    )
