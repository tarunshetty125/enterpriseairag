from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.serializers import (
    serialize_customer_detail,
    serialize_customer_list_item,
    serialize_features,
)
from app.datasets.service import DatasetService
from app.db.session import get_db_session
from app.schemas.customers import (
    CustomerDetailResponse,
    CustomerFeaturesResponse,
    CustomerListResponse,
)

router = APIRouter(prefix="/customers", tags=["customers"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("", response_model=CustomerListResponse)
def list_customers(
    session: DbSession,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> CustomerListResponse:
    service = DatasetService(session)
    return CustomerListResponse(
        total=service.customer_count(),
        items=[
            serialize_customer_list_item(customer)
            for customer in service.list_customers(limit=limit, offset=offset)
        ],
    )


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
def get_customer(
    customer_id: str,
    session: DbSession,
) -> CustomerDetailResponse:
    service = DatasetService(session)
    customer = service.get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return serialize_customer_detail(
        customer,
        service.latest_feature_snapshot(customer.customer_id),
    )


@router.get("/{customer_id}/features", response_model=CustomerFeaturesResponse)
def get_customer_features(
    customer_id: str,
    session: DbSession,
) -> CustomerFeaturesResponse:
    service = DatasetService(session)
    customer = service.get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return serialize_features(customer_id, service.latest_feature_snapshot(customer_id))
