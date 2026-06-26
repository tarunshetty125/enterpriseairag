from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.datasets.catalog import DATASET_CATALOG
from app.datasets.quality import DataQualityService
from app.datasets.seeder import DatasetSeeder
from app.datasets.types import IngestionSummary, QualityReport
from app.feature_store.service import FeatureStoreService
from app.models.canonical import (
    Customer,
    DatasetMetadata,
    FeatureSnapshot,
    IngestionRun,
    Loan,
    Product,
    Transaction,
)


@dataclass(frozen=True)
class IngestionResult:
    summaries: list[IngestionSummary]
    feature_snapshots_generated: int
    quality_report: QualityReport


class DatasetService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_datasets(self) -> list[DatasetMetadata]:
        return list(
            self.session.scalars(
                select(DatasetMetadata).order_by(DatasetMetadata.dataset_name)
            )
        )

    def status(self) -> dict[str, Any]:
        settings = get_settings()
        latest_run = self.session.scalar(
            select(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(1)
        )
        dataset_count = (
            self.session.scalar(select(func.count(DatasetMetadata.dataset_name))) or 0
        )
        rows_loaded = self.session.scalar(select(func.sum(DatasetMetadata.rows))) or 0
        sqlite_path = settings.database.sqlite_path
        return {
            "configured_datasets": len(DATASET_CATALOG),
            "loaded_datasets": dataset_count,
            "rows_loaded": rows_loaded,
            "sqlite_path": sqlite_path.as_posix(),
            "sqlite_size_bytes": self._file_size(sqlite_path),
            "latest_ingestion": latest_run,
        }

    def list_customers(self, limit: int = 100, offset: int = 0) -> list[Customer]:
        return list(
            self.session.scalars(
                select(Customer)
                .order_by(Customer.customer_id)
                .offset(offset)
                .limit(min(limit, 500))
            )
        )

    def customer_count(self) -> int:
        return self.session.scalar(select(func.count(Customer.customer_id))) or 0

    def get_customer(self, customer_id: str) -> Customer | None:
        return self.session.scalar(
            select(Customer)
            .where(Customer.customer_id == customer_id)
            .options(
                selectinload(Customer.loans),
                selectinload(Customer.products),
                selectinload(Customer.transactions),
                selectinload(Customer.feature_snapshots),
            )
        )

    def latest_feature_snapshot(self, customer_id: str) -> FeatureSnapshot | None:
        return FeatureStoreService(self.session).latest_for_customer(customer_id)

    def table_counts(self) -> dict[str, int]:
        return {
            "customers": self.session.scalar(select(func.count(Customer.customer_id)))
            or 0,
            "loans": self.session.scalar(select(func.count(Loan.id))) or 0,
            "transactions": self.session.scalar(select(func.count(Transaction.id)))
            or 0,
            "products": self.session.scalar(select(func.count(Product.id))) or 0,
            "feature_snapshots": self.session.scalar(
                select(func.count(FeatureSnapshot.id))
            )
            or 0,
            "dataset_metadata": self.session.scalar(
                select(func.count(DatasetMetadata.dataset_name))
            )
            or 0,
            "ingestion_runs": self.session.scalar(select(func.count(IngestionRun.id)))
            or 0,
        }

    def _file_size(self, path: Path) -> int:
        if not path.exists():
            return 0
        return path.stat().st_size


class SeedService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def ingest_all(self) -> IngestionResult:
        summaries = DatasetSeeder(self.session).ingest_all()
        feature_count = FeatureStoreService(self.session).generate_snapshots()
        quality_report = DataQualityService(self.session).report()
        return IngestionResult(
            summaries=summaries,
            feature_snapshots_generated=feature_count,
            quality_report=quality_report,
        )
