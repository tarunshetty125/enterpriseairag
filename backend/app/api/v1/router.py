from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import (
    customers,
    data_quality,
    datasets,
    feature_store,
    health,
    intelligence,
    ml,
    settings,
    system_health,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(system_health.router)
api_router.include_router(settings.router)
api_router.include_router(datasets.router)
api_router.include_router(customers.router)
api_router.include_router(data_quality.router)
api_router.include_router(feature_store.router)
api_router.include_router(ml.router)
api_router.include_router(intelligence.router)
