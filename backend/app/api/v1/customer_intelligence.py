from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.intelligence.report_service import CustomerIntelligenceService
from app.schemas.intelligence import (
    CustomerIntelligenceReportRequest,
    CustomerIntelligenceReportResponse,
    RecentReportsResponse,
    ShowcaseMetricsResponse,
    WorkflowStageResponse,
)

router = APIRouter(tags=["customer-intelligence"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.post(
    "/customers/{customer_id}/intelligence-report",
    response_model=CustomerIntelligenceReportResponse,
)
def generate_customer_intelligence_report(
    customer_id: str,
    request: CustomerIntelligenceReportRequest,
    session: DbSession,
) -> CustomerIntelligenceReportResponse:
    try:
        result = CustomerIntelligenceService(session).generate_report(
            customer_id,
            force_regenerate=request.force_regenerate,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return CustomerIntelligenceReportResponse.model_validate(result)


@router.get(
    "/customers/{customer_id}/intelligence-report",
    response_model=CustomerIntelligenceReportResponse,
)
def get_customer_intelligence_report(
    customer_id: str,
    session: DbSession,
) -> CustomerIntelligenceReportResponse:
    report = CustomerIntelligenceService(session).latest_report(customer_id)
    if report is None:
        raise HTTPException(
            status_code=404, detail="Customer intelligence report not found"
        )
    return CustomerIntelligenceReportResponse.model_validate(report)


@router.get(
    "/customers/{customer_id}/workflow-trace",
    response_model=list[WorkflowStageResponse],
)
def get_customer_workflow_trace(
    customer_id: str,
    session: DbSession,
) -> list[WorkflowStageResponse]:
    return [
        WorkflowStageResponse.model_validate(stage)
        for stage in CustomerIntelligenceService(session).workflow_trace(customer_id)
    ]


@router.get("/customers/{customer_id}/intelligence-report/export")
def export_customer_intelligence_report(
    customer_id: str,
    session: DbSession,
    format: Annotated[str, Query(pattern="^(pdf|markdown|json)$")] = "pdf",
) -> Response:
    try:
        exported = CustomerIntelligenceService(session).export_report(
            customer_id,
            format,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(
        content=exported.content,
        media_type=exported.media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{exported.filename}"',
        },
    )


@router.get(
    "/intelligence/reports/recent",
    response_model=RecentReportsResponse,
)
def get_recent_intelligence_reports(
    session: DbSession,
) -> RecentReportsResponse:
    reports = CustomerIntelligenceService(session).recent_reports()
    return RecentReportsResponse(
        reports=[
            CustomerIntelligenceReportResponse.model_validate(report)
            for report in reports
        ]
    )


@router.get(
    "/intelligence/showcase-metrics",
    response_model=ShowcaseMetricsResponse,
)
def get_showcase_metrics(session: DbSession) -> ShowcaseMetricsResponse:
    metrics = CustomerIntelligenceService(session).showcase_metrics()
    return ShowcaseMetricsResponse.model_validate(metrics)
