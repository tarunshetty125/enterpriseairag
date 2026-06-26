from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.datasets.quality import DataQualityService
from app.db.session import get_db_session
from app.schemas.data_quality import QualityCheckResponse, QualityReportResponse

router = APIRouter(prefix="/data-quality", tags=["data-quality"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("", response_model=QualityReportResponse)
def get_data_quality(
    session: DbSession,
) -> QualityReportResponse:
    report = DataQualityService(session).report()
    return QualityReportResponse(
        score=report.score,
        checks=[
            QualityCheckResponse(
                name=check.name,
                status=check.status,
                affected_rows=check.affected_rows,
                details=check.details,
            )
            for check in report.checks
        ],
    )
