from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.datasets.service import DatasetService, SeedService  # noqa: E402
from app.db.session import SessionLocal, initialize_database  # noqa: E402


def main() -> None:
    initialize_database()
    with SessionLocal() as session:
        result = SeedService(session).ingest_all()
        counts = DatasetService(session).table_counts()
        print("Ingestion status:", result.quality_report.score)
        print("Feature snapshots:", result.feature_snapshots_generated)
        print("Table counts:", counts)
        for summary in result.summaries:
            print(
                summary.dataset_name,
                summary.status,
                summary.rows_processed,
                summary.message,
            )


if __name__ == "__main__":
    main()
