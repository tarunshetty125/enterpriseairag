from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.providers.manager import ProviderManager
from app.schemas.ai import AIProcessingSettingsResponse

router = APIRouter(prefix="/settings", tags=["settings"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/ai-processing", response_model=AIProcessingSettingsResponse)
def get_ai_processing_settings(session: DbSession) -> AIProcessingSettingsResponse:
    return AIProcessingSettingsResponse.model_validate(
        ProviderManager(session).current_settings()
    )
