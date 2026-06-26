from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.settings import AIProcessingSettingsResponse

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/ai-processing", response_model=AIProcessingSettingsResponse)
def get_ai_processing_settings() -> AIProcessingSettingsResponse:
    settings = get_settings()
    return AIProcessingSettingsResponse.model_validate(settings.ai)
