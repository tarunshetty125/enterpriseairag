"""Provider API routes.

Runtime provider switching, model listing, health checks, and settings.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.gateway.metrics import MetricsCollector
from app.providers.manager import ProviderManager
from app.schemas.ai import (
    AIModelResponse,
    AIProcessingSettingsResponse,
    ProviderListResponse,
    ProviderModelsResponse,
    ProviderResponse,
    ProviderSettingsPatch,
    ProviderStatusResponse,
    ProviderSwitchRequest,
)

router = APIRouter(prefix="/providers", tags=["providers"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("", response_model=ProviderListResponse)
def list_providers(session: DbSession) -> ProviderListResponse:
    manager = ProviderManager(session)
    return ProviderListResponse(
        providers=[
            ProviderResponse(
                name=item.name,
                status=item.status,
                configured=item.configured,
                active=item.active,
                latency_ms=item.latency_ms,
                details=item.details,
            )
            for item in manager.list_providers()
        ]
    )


@router.get("/models", response_model=ProviderModelsResponse)
def list_provider_models(
    session: DbSession,
    provider: Annotated[str | None, Query()] = None,
) -> ProviderModelsResponse:
    manager = ProviderManager(session)
    provider_name = provider or manager.current_settings().provider
    return ProviderModelsResponse(
        provider=provider_name,
        models=[
            AIModelResponse(
                id=model.id,
                name=model.name,
                context_window=model.context_window,
                supports_streaming=model.supports_streaming,
            )
            for model in manager.list_models(provider_name)
        ],
    )


@router.post("/switch", response_model=AIProcessingSettingsResponse)
def switch_provider(
    request: ProviderSwitchRequest,
    session: DbSession,
) -> AIProcessingSettingsResponse:
    try:
        settings = ProviderManager(session).switch_provider(
            request.provider,
            request.model,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return AIProcessingSettingsResponse.model_validate(settings)


@router.get("/status", response_model=ProviderStatusResponse)
def provider_status(session: DbSession) -> ProviderStatusResponse:
    manager = ProviderManager(session)
    return ProviderStatusResponse(
        settings=AIProcessingSettingsResponse.model_validate(
            manager.current_settings()
        ),
        providers=[
            ProviderResponse(
                name=item.name,
                status=item.status,
                configured=item.configured,
                active=item.active,
                latency_ms=item.latency_ms,
                details=item.details,
            )
            for item in manager.list_providers()
        ],
        metrics=MetricsCollector(session).status(),
        switch_events=[
            {
                "provider": event.provider,
                "model": event.model,
                "previous_provider": event.previous_provider,
                "previous_model": event.previous_model,
                "created_at": event.created_at,
            }
            for event in manager.latest_switches()
        ],
    )


@router.patch("/settings", response_model=AIProcessingSettingsResponse)
def patch_provider_settings(
    request: ProviderSettingsPatch,
    session: DbSession,
) -> AIProcessingSettingsResponse:
    settings = ProviderManager(session).update_settings(**request.model_dump())
    return AIProcessingSettingsResponse.model_validate(settings)
