from __future__ import annotations

import csv
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.datasets.catalog import DATASET_CATALOG, DatasetDefinition
from app.datasets.loader import DatasetLoader
from app.datasets.mapper import DatasetMapper
from app.datasets.normalizer import DatasetNormalizer
from app.datasets.types import CanonicalBatch, IngestionSummary
from app.datasets.validator import DatasetValidator
from app.models.canonical import (
    Customer,
    DatasetMetadata,
    IngestionRun,
    Loan,
    Product,
    Transaction,
)


class DatasetSeeder:
    """Coordinates loading, validation, normalization, mapping, and persistence."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.loader = DatasetLoader()
        self.validator = DatasetValidator()
        self.normalizer = DatasetNormalizer()
        self.mapper = DatasetMapper(session)
        settings = get_settings()
        self.processed_path = settings.data.processed_path
        self.processed_path.mkdir(parents=True, exist_ok=True)

    def ingest_all(self) -> list[IngestionSummary]:
        summaries: list[IngestionSummary] = []
        for definition in DATASET_CATALOG:
            summaries.append(self.ingest_dataset(definition))
        return summaries

    def ingest_dataset(self, definition: DatasetDefinition) -> IngestionSummary:
        started_at = datetime.now(UTC)
        run = IngestionRun(
            dataset_name=definition.name,
            status="running",
            rows_processed=0,
            message=None,
        )
        self.session.add(run)
        self.session.flush()

        rows, columns, checksum = self.loader.load_csv(definition)
        validation = self.validator.validate(definition, rows, columns)
        if not validation.is_valid:
            message = "Missing columns: " + ", ".join(validation.missing_columns)
            run.status = "failed"
            run.finished_at = datetime.now(UTC)
            run.message = message
            self.session.commit()
            return IngestionSummary(
                dataset_name=definition.name,
                status="failed",
                rows_processed=0,
                checksum=checksum,
                started_at=started_at,
                finished_at=run.finished_at,
                message=message,
            )

        normalized_rows = self.normalizer.normalize_rows(rows)
        self._write_processed_csv(definition, normalized_rows)
        batch = self.mapper.map(definition.name, normalized_rows)
        self._persist_batch(batch)
        metadata = DatasetMetadata(
            dataset_name=definition.name,
            source=definition.source,
            version=definition.version,
            rows=len(rows),
            columns=columns,
            imported_at=datetime.now(UTC),
            checksum=checksum,
            status="loaded",
        )
        self.session.merge(metadata)

        run.status = "completed"
        run.rows_processed = len(rows)
        run.finished_at = datetime.now(UTC)
        run.message = "Dataset ingested into canonical schema"
        self.session.commit()

        return IngestionSummary(
            dataset_name=definition.name,
            status="completed",
            rows_processed=len(rows),
            checksum=checksum,
            started_at=started_at,
            finished_at=run.finished_at,
            message=run.message,
        )

    def _write_processed_csv(
        self,
        definition: DatasetDefinition,
        rows: list[dict[str, str]],
    ) -> Path:
        path = self.processed_path / definition.filename
        if not rows:
            path.write_text("", encoding="utf-8")
            return path

        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        return path

    def _persist_batch(self, batch: CanonicalBatch) -> None:
        for record in batch.customers:
            existing = self.session.get(Customer, record.customer_id)
            if existing is None:
                self.session.add(Customer(**record.__dict__))
            else:
                self._merge_customer(existing, record)

        self.session.flush()

        for loan_record in batch.loans:
            self._upsert_child(
                Loan,
                loan_record.source_dataset,
                loan_record.source_record_id,
                loan_record.__dict__,
            )
        for product_record in batch.products:
            self._upsert_child(
                Product,
                product_record.source_dataset,
                product_record.source_record_id,
                product_record.__dict__,
            )
        for transaction_record in batch.transactions:
            self._upsert_child(
                Transaction,
                transaction_record.source_dataset,
                transaction_record.source_record_id,
                transaction_record.__dict__,
            )

    def _merge_customer(self, existing: Customer, record: object) -> None:
        values = record.__dict__
        for field_name, value in values.items():
            if field_name in {"customer_id", "source_dataset", "source_record_id"}:
                continue
            if field_name == "external_references" and isinstance(value, dict):
                existing.external_references = {
                    **dict(existing.external_references or {}),
                    **value,
                }
                continue
            if value is not None:
                setattr(existing, field_name, value)

    def _upsert_child(
        self,
        model: type[Loan] | type[Product] | type[Transaction],
        source_dataset: str,
        source_record_id: str,
        values: dict[str, object],
    ) -> None:
        existing = self.session.scalar(
            select(model).where(
                model.source_dataset == source_dataset,
                model.source_record_id == source_record_id,
            )
        )
        if existing is None:
            self.session.add(model(**values))
            return
        for field_name, value in values.items():
            setattr(existing, field_name, value)
