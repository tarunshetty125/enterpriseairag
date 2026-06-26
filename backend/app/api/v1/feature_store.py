from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.feature_store.service import FeatureStoreService
from app.schemas.feature_store import FeatureStoreStatusResponse

router = APIRouter(prefix="/feature-store", tags=["feature-store"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/status", response_model=FeatureStoreStatusResponse)
def get_feature_store_status(
    session: DbSession,
) -> FeatureStoreStatusResponse:
    return FeatureStoreStatusResponse(**FeatureStoreService(session).status())
