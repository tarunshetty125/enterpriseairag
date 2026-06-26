from __future__ import annotations

from app.datasets.mapper import DatasetMapper
from app.datasets.types import CanonicalCustomerRecord
from app.datasets.utils import build_customer_id
from app.feature_store.service import FeatureStoreService
from app.models.canonical import Customer, DatasetMetadata
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_synthetic_customer_id_is_deterministic() -> None:
    first = build_customer_id("bank_customer_churn", "15634602")
    second = build_customer_id("bank_customer_churn", "15634602")

    assert first == second
    assert first.startswith("CUST-")


def test_bank_churn_mapper_creates_canonical_customer(session: Session) -> None:
    batch = DatasetMapper(session).map(
        "bank_customer_churn",
        [
            {
                "customer_id": "15634602",
                "surname": "Hargrave",
                "credit_score": "619",
                "geography": "France",
                "gender": "Female",
                "age": "42",
                "tenure": "2",
                "balance": "0",
                "num_of_products": "1",
                "has_cr_card": "1",
                "is_active_member": "1",
                "estimated_salary": "101348.88",
                "exited": "1",
            }
        ],
    )

    assert len(batch.customers) == 1
    assert batch.customers[0].customer_id == build_customer_id(
        "bank_customer_churn", "15634602"
    )
    assert batch.customers[0].credit_score == 619
    assert batch.products[0].product_type == "Credit Card"


def test_feature_store_generates_snapshot(session: Session) -> None:
    customer = Customer(
        **CanonicalCustomerRecord(
            customer_id="CUST-TEST",
            full_name="Test Customer",
            gender="Female",
            age=42,
            geography="France",
            education=None,
            marital_status=None,
            income_category="Upper Middle",
            estimated_income=100000.0,
            credit_score=720,
            savings_balance=25000.0,
            tenure_months=36,
            source_dataset="unit_test",
            source_record_id="unit-test-1",
            external_references={},
        ).__dict__
    )
    session.add(customer)
    session.add(
        DatasetMetadata(
            dataset_name="unit_test",
            source="unit",
            version="unit-v1",
            rows=1,
            columns=["customer_id"],
            checksum="abc",
            status="loaded",
        )
    )
    session.commit()

    generated = FeatureStoreService(session).generate_snapshots()
    snapshot = FeatureStoreService(session).latest_for_customer("CUST-TEST")

    assert generated == 1
    assert snapshot is not None
    assert snapshot.features["values"]["savings_ratio"] == 0.25
    assert snapshot.feature_version == "features_v1"


def test_customers_api_returns_real_database_data(
    client: TestClient,
    session: Session,
) -> None:
    session.add(
        Customer(
            **CanonicalCustomerRecord(
                customer_id="CUST-API",
                full_name="API Customer",
                gender="Male",
                age=38,
                geography="Urban",
                education="Graduate",
                marital_status="Yes",
                income_category="Middle",
                estimated_income=75000.0,
                credit_score=700,
                savings_balance=10000.0,
                tenure_months=24,
                source_dataset="unit_test",
                source_record_id="api-1",
                external_references={},
            ).__dict__
        )
    )
    session.commit()

    response = client.get("/api/v1/customers")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["customerId"] == "CUST-API"
