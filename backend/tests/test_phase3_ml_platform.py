from __future__ import annotations

from pathlib import Path

from app.feature_store.service import FeatureStoreService
from app.ml.models.artifact_store import ModelArtifactStore
from app.ml.pipelines.risk import RiskPipeline
from app.ml.pipelines.segmentation import SegmentationPipeline
from app.models.canonical import Customer, DatasetMetadata, Loan
from app.models.ml import MLModelRegistry
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session


def test_phase3_training_registry_and_prediction_api(
    client: TestClient,
    session: Session,
    tmp_path: Path,
) -> None:
    _seed_ml_customers(session)
    generated = FeatureStoreService(session).generate_snapshots()
    artifact_store = ModelArtifactStore(tmp_path)

    risk_model = RiskPipeline(session, artifact_store=artifact_store).train()
    segment_model = SegmentationPipeline(session, artifact_store=artifact_store).train()

    assert generated == 15
    assert Path(risk_model.artifact_path).exists()
    assert Path(segment_model.artifact_path).exists()
    assert risk_model.active_model == 1
    assert segment_model.active_model == 1
    assert risk_model.accuracy is not None

    registry_rows = list(session.scalars(select(MLModelRegistry)))
    assert len(registry_rows) == 2

    models_response = client.get("/api/v1/ml/models")
    assert models_response.status_code == 200
    assert len(models_response.json()["models"]) == 2

    risk_response = client.post(
        "/api/v1/ml/predict/risk",
        json={"customerId": "CUST-HIGH-0"},
    )
    assert risk_response.status_code == 200
    risk_payload = risk_response.json()
    assert risk_payload["riskLevel"] in {"Low", "Medium", "High"}
    assert risk_payload["confidence"] >= 0
    assert risk_payload["topFeatures"]

    segment_response = client.post(
        "/api/v1/ml/predict/segment",
        json={"customerId": "CUST-LOW-0"},
    )
    assert segment_response.status_code == 200
    assert segment_response.json()["segmentLabel"] in {
        "Premium",
        "High Value",
        "Budget",
        "Young Investors",
        "Loan Focused",
    }

    importance_response = client.get("/api/v1/ml/feature-importance")
    assert importance_response.status_code == 200
    assert importance_response.json()["features"]


def _seed_ml_customers(session: Session) -> None:
    session.add(
        DatasetMetadata(
            dataset_name="ml_unit_test",
            source="unit",
            version="ml-v1",
            rows=15,
            columns=["customer_id"],
            checksum="ml-checksum",
            status="loaded",
        )
    )
    for index in range(5):
        session.add(
            Customer(
                customer_id=f"CUST-LOW-{index}",
                full_name=f"Low Risk {index}",
                gender="Female",
                age=44 + index,
                geography="Urban",
                education="Graduate",
                marital_status="Married",
                income_category="High",
                estimated_income=150000.0,
                credit_score=760,
                savings_balance=90000.0,
                tenure_months=72,
                source_dataset="ml_unit_test",
                source_record_id=f"low-{index}",
                external_references={},
            )
        )
        medium_customer_id = f"CUST-MEDIUM-{index}"
        session.add(
            Customer(
                customer_id=medium_customer_id,
                full_name=f"Medium Risk {index}",
                gender="Male",
                age=36 + index,
                geography="Suburban",
                education="Graduate",
                marital_status="Single",
                income_category="Middle",
                estimated_income=80000.0,
                credit_score=665,
                savings_balance=5000.0,
                tenure_months=30,
                source_dataset="ml_unit_test",
                source_record_id=f"medium-{index}",
                external_references={},
            )
        )
        session.add(
            Loan(
                customer_id=medium_customer_id,
                loan_type="Personal Loan",
                amount=60000.0,
                term_months=48,
                status="approved",
                credit_history=1.0,
                property_area="Urban",
                source_dataset="ml_unit_test",
                source_record_id=f"medium-loan-{index}",
            )
        )
        high_customer_id = f"CUST-HIGH-{index}"
        session.add(
            Customer(
                customer_id=high_customer_id,
                full_name=f"High Risk {index}",
                gender="Male",
                age=28 + index,
                geography="Rural",
                education="Not Graduate",
                marital_status="Single",
                income_category="Low",
                estimated_income=50000.0,
                credit_score=540,
                savings_balance=1000.0,
                tenure_months=8,
                source_dataset="ml_unit_test",
                source_record_id=f"high-{index}",
                external_references={},
            )
        )
        session.add(
            Loan(
                customer_id=high_customer_id,
                loan_type="Home Loan",
                amount=250000.0,
                term_months=240,
                status="rejected",
                credit_history=0.0,
                property_area="Rural",
                source_dataset="ml_unit_test",
                source_record_id=f"high-loan-{index}",
            )
        )
    session.commit()
