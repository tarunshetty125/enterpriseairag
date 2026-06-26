from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter

from app.core.config import get_settings
from app.db.health import check_database_health
from app.schemas.health import ComponentHealth, SystemHealthResponse

router = APIRouter(tags=["system-health"])


@router.get("/system-health", response_model=SystemHealthResponse)
def system_health() -> SystemHealthResponse:
    settings = get_settings()
    database_health = check_database_health()
    components = [
        ComponentHealth(name="api", status="ok", details="FastAPI application ready"),
        ComponentHealth(
            name="sqlite",
            status=database_health.status,
            details=database_health.details,
        ),
        ComponentHealth(
            name="ai_configuration",
            status="configured",
            details=f"{settings.ai.provider}:{settings.ai.model}",
        ),
    ]
    overall_status = (
        "ok" if all(item.status != "error" for item in components) else "error"
    )

    return SystemHealthResponse(
        status=overall_status,
        application=settings.app.name,
        version=settings.app.version,
        environment=settings.app.environment,
        components=components,
        timestamp=datetime.now(UTC),
    )
