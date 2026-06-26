from __future__ import annotations

from typing import Any

from app.ml.pipelines.prediction import RiskPredictionResult, SegmentPredictionResult
from app.ml.prediction.explainability import FeatureContribution
from app.ml.registry.service import ModelRegistryService
from app.models.canonical import (
    Customer,
    DatasetMetadata,
    FeatureSnapshot,
    IngestionRun,
    Loan,
    Product,
    Transaction,
)
from app.models.ml import MLModelRegistry
from app.schemas.customers import (
    CustomerDetailResponse,
    CustomerFeaturesResponse,
    CustomerListItemResponse,
    FeatureItemResponse,
    LoanResponse,
    ProductResponse,
    TransactionResponse,
)
from app.schemas.datasets import DatasetMetadataResponse, IngestionRunResponse
from app.schemas.ml import (
    FeatureContributionResponse,
    ModelRegistryItemResponse,
    RiskPredictionResponse,
    SegmentPredictionResponse,
)


def serialize_dataset_metadata(item: DatasetMetadata) -> DatasetMetadataResponse:
    return DatasetMetadataResponse(
        dataset_name=item.dataset_name,
        source=item.source,
        version=item.version,
        rows=item.rows,
        columns=list(item.columns),
        imported_at=item.imported_at,
        checksum=item.checksum,
        status=item.status,
    )


def serialize_ingestion_run(run: IngestionRun | None) -> IngestionRunResponse | None:
    if run is None:
        return None
    return IngestionRunResponse(
        id=run.id,
        dataset_name=run.dataset_name,
        started_at=run.started_at,
        finished_at=run.finished_at,
        status=run.status,
        rows_processed=run.rows_processed,
        message=run.message,
    )


def serialize_customer_list_item(customer: Customer) -> CustomerListItemResponse:
    return CustomerListItemResponse(
        customer_id=customer.customer_id,
        full_name=customer.full_name,
        gender=customer.gender,
        age=customer.age,
        geography=customer.geography,
        income_category=customer.income_category,
        estimated_income=customer.estimated_income,
        credit_score=customer.credit_score,
        source_dataset=customer.source_dataset,
    )


def serialize_features(
    customer_id: str,
    snapshot: FeatureSnapshot | None,
) -> CustomerFeaturesResponse:
    if snapshot is None:
        return CustomerFeaturesResponse(customer_id=customer_id, features=[])

    payload = snapshot.features
    values = _dict_value(payload.get("values"))
    descriptions = _dict_value(payload.get("descriptions"))
    features = [
        FeatureItemResponse(
            name=name,
            value=value,
            description=str(descriptions.get(name, "")),
            version=snapshot.feature_version,
            dataset_version=snapshot.dataset_version,
            generated_at=snapshot.generated_at,
        )
        for name, value in values.items()
    ]
    return CustomerFeaturesResponse(customer_id=customer_id, features=features)


def serialize_customer_detail(
    customer: Customer,
    snapshot: FeatureSnapshot | None,
) -> CustomerDetailResponse:
    list_item = serialize_customer_list_item(customer)
    return CustomerDetailResponse(
        **list_item.model_dump(),
        education=customer.education,
        marital_status=customer.marital_status,
        savings_balance=customer.savings_balance,
        tenure_months=customer.tenure_months,
        external_references=dict(customer.external_references or {}),
        loans=[serialize_loan(loan) for loan in customer.loans],
        transactions=[
            serialize_transaction(transaction)
            for transaction in sorted(customer.transactions, key=lambda item: item.id)[
                :100
            ]
        ],
        products=[serialize_product(product) for product in customer.products],
        features=serialize_features(customer.customer_id, snapshot).features,
    )


def serialize_loan(loan: Loan) -> LoanResponse:
    return LoanResponse(
        id=loan.id,
        loan_type=loan.loan_type,
        amount=loan.amount,
        term_months=loan.term_months,
        status=loan.status,
        credit_history=loan.credit_history,
        property_area=loan.property_area,
    )


def serialize_transaction(transaction: Transaction) -> TransactionResponse:
    return TransactionResponse(
        id=transaction.id,
        step=transaction.step,
        transaction_type=transaction.transaction_type,
        category=transaction.category,
        direction=transaction.direction,
        amount=transaction.amount,
        description=transaction.description,
        counterparty=transaction.counterparty,
        is_fraud=transaction.is_fraud,
    )


def serialize_product(product: Product) -> ProductResponse:
    return ProductResponse(
        id=product.id,
        product_type=product.product_type,
        status=product.status,
        credit_limit=product.credit_limit,
        revolving_balance=product.revolving_balance,
        revenue=product.revenue,
    )


def serialize_model_registry_item(
    model: MLModelRegistry,
    registry: ModelRegistryService,
) -> ModelRegistryItemResponse:
    return ModelRegistryItemResponse(
        id=model.id,
        model_name=model.model_name,
        version=model.version,
        algorithm=model.algorithm,
        training_date=model.training_date,
        metrics=dict(model.metrics or {}),
        accuracy=model.accuracy,
        precision=model.precision,
        recall=model.recall,
        f1=model.f1,
        features_used=list(model.features_used or []),
        artifact_path=model.artifact_path,
        dataset_version=model.dataset_version,
        feature_version=model.feature_version,
        active_model=bool(model.active_model),
        training_time_ms=model.training_time_ms,
        inference_time_ms=model.inference_time_ms,
        training_metadata=dict(model.training_metadata or {}),
        prediction_count=registry.prediction_count(model.id),
    )


def serialize_risk_prediction(
    prediction: RiskPredictionResult,
) -> RiskPredictionResponse:
    return RiskPredictionResponse(
        customer_id=prediction.customer_id,
        risk_level=prediction.risk_level,
        confidence=prediction.confidence,
        probabilities=prediction.probabilities,
        top_features=[
            serialize_feature_contribution(feature)
            for feature in prediction.top_features
        ],
        business_explanation=prediction.business_explanation,
        model_version=prediction.model_version,
        inference_time_ms=prediction.inference_time_ms,
    )


def serialize_segment_prediction(
    prediction: SegmentPredictionResult,
) -> SegmentPredictionResponse:
    return SegmentPredictionResponse(
        customer_id=prediction.customer_id,
        segment_label=prediction.segment_label,
        confidence=prediction.confidence,
        nearest_distance=prediction.nearest_distance,
        centroid_summary=prediction.centroid_summary,
        model_version=prediction.model_version,
        inference_time_ms=prediction.inference_time_ms,
    )


def serialize_feature_contribution(
    feature: FeatureContribution,
) -> FeatureContributionResponse:
    return FeatureContributionResponse(
        name=feature.name,
        value=feature.value,
        importance=feature.importance,
        description=feature.description,
    )


def _dict_value(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}
