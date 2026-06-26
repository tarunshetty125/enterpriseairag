from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.schemas.settings import to_camel


class QualityCheckResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str
    status: str
    affected_rows: int
    details: str


class QualityReportResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    score: float
    checks: list[QualityCheckResponse]
