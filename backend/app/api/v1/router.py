from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import health, settings, system_health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(system_health.router)
api_router.include_router(settings.router)
