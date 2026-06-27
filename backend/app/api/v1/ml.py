"""Machine Learning API routes.

Model training, prediction, registry, evaluation, and feature importance.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.serializers import (
    serialize_feature_contribution,
    serialize_model_registry_item,
    serialize_risk_prediction,
    serialize_segment_prediction,
)
from app.db.session import get_db_session
from app.ml.evaluation.service import MLEvaluationService
from app.ml.pipelines.prediction import PredictionPipeline
from app.ml.registry.service import ModelRegistryService
from app.ml.training.service import MLTrainingService
from app.schemas.ml import (
    EvaluationResponse,
    FeatureImportanceResponse,
    ModelRegistryItemResponse,
    ModelRegistryListResponse,
    RiskPredictionRequest,
    RiskPredictionResponse,
    SegmentPredictionRequest,
    SegmentPredictionResponse,
    TrainModelResponse,
)

router = APIRouter(prefix="/ml", tags=["machine-learning"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.post("/train/risk", response_model=TrainModelResponse)
def train_risk_model(session: DbSession) -> TrainModelResponse:
    try:
        model = MLTrainingService(session).train_risk_model()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    registry = ModelRegistryService(session)
    return TrainModelResponse(
        model=serialize_model_registry_item(model, registry),
        message="Risk model trained and registered.",
    )


@router.post("/train/segmentation", response_model=TrainModelResponse)
def train_segmentation_model(session: DbSession) -> TrainModelResponse:
    try:
        model = MLTrainingService(session).train_segmentation_model()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    registry = ModelRegistryService(session)
    return TrainModelResponse(
        model=serialize_model_registry_item(model, registry),
        message="Segmentation model trained and registered.",
    )


@router.get("/models", response_model=ModelRegistryListResponse)
def list_models(session: DbSession) -> ModelRegistryListResponse:
    registry = ModelRegistryService(session)
    return ModelRegistryListResponse(
        models=[
            serialize_model_registry_item(model, registry)
            for model in registry.list_models()
        ]
    )


@router.post("/models/{model_id}/activate", response_model=ModelRegistryItemResponse)
def activate_model(model_id: int, session: DbSession) -> ModelRegistryItemResponse:
    registry = ModelRegistryService(session)
    model = registry.activate(model_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return serialize_model_registry_item(model, registry)


@router.get("/models/{model}", response_model=ModelRegistryItemResponse)
def get_model(model: str, session: DbSession) -> ModelRegistryItemResponse:
    registry = ModelRegistryService(session)
    registered_model = registry.get_model(model)
    if registered_model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return serialize_model_registry_item(registered_model, registry)


@router.post("/predict/risk", response_model=RiskPredictionResponse)
def predict_risk(
    request: RiskPredictionRequest,
    session: DbSession,
) -> RiskPredictionResponse:
    try:
        prediction = PredictionPipeline(session).predict_risk(request.customer_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return serialize_risk_prediction(prediction)


@router.post("/predict/segment", response_model=SegmentPredictionResponse)
def predict_segment(
    request: SegmentPredictionRequest,
    session: DbSession,
) -> SegmentPredictionResponse:
    try:
        prediction = PredictionPipeline(session).predict_segment(request.customer_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return serialize_segment_prediction(prediction)


@router.get("/evaluation", response_model=EvaluationResponse)
def get_evaluation(session: DbSession) -> EvaluationResponse:
    summary = MLEvaluationService(session).summary()
    return EvaluationResponse(
        risk=summary["risk"],
        segmentation=summary["segmentation"],
    )


@router.get("/feature-importance", response_model=FeatureImportanceResponse)
def get_feature_importance(
    session: DbSession,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> FeatureImportanceResponse:
    try:
        model, features = PredictionPipeline(session).feature_importance(limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return FeatureImportanceResponse(
        model_name=model.model_name,
        model_version=model.version,
        features=[serialize_feature_contribution(feature) for feature in features],
    )
