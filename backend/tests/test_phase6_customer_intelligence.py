from __future__ import annotations

from pathlib import Path

from app.feature_store.service import FeatureStoreService
from app.ml.models.artifact_store import ModelArtifactStore
from app.ml.pipelines.risk import RiskPipeline
from app.ml.pipelines.segmentation import SegmentationPipeline
from app.models.canonical import Customer, DatasetMetadata, Loan, Product, Transaction
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_phase6_customer_intelligence_report_trace_and_exports(
    client: TestClient,
    session: Session,
    tmp_path: Path,
) -> None:
    _seed_final_customers(session)
    FeatureStoreService(session).generate_snapshots()
    artifact_store = ModelArtifactStore(tmp_path)
    RiskPipeline(session, artifact_store=artifact_store).train()
    SegmentationPipeline(session, artifact_store=artifact_store).train()

    settings = client.patch(
        "/api/v1/providers/settings",
        json={"similarityThreshold": 0.0, "retrievalTopK": 4},
    )
    assert settings.status_code == 200

    generated = client.post(
        "/api/v1/customers/CUST-FINAL/intelligence-report",
        json={"forceRegenerate": False},
    )
    assert generated.status_code == 200
    payload = generated.json()
    assert payload["customerId"] == "CUST-FINAL"
    assert payload["report"]["executive_summary"]
    assert payload["report"]["risk_assessment"]["current_risk"] in {
        "Low",
        "Medium",
        "High",
    }
    assert payload["report"]["product_recommendations"]
    assert payload["report"]["policy_validation"]["citations"]
    assert payload["report"]["explainability"]["feature_importance"]
    assert payload["workflowTrace"]
    assert payload["retrievedChunks"] >= 1

    cached = client.post(
        "/api/v1/customers/CUST-FINAL/intelligence-report",
        json={"forceRegenerate": False},
    )
    assert cached.status_code == 200
    assert cached.json()["cacheHit"] is True

    trace = client.get("/api/v1/customers/CUST-FINAL/workflow-trace")
    assert trace.status_code == 200
    assert any(stage["stage"] == "RAG" for stage in trace.json())

    metrics = client.get("/api/v1/intelligence/showcase-metrics")
    assert metrics.status_code == 200
    assert metrics.json()["reportCount"] >= 1
    assert metrics.json()["recentReports"]

    markdown = client.get(
        "/api/v1/customers/CUST-FINAL/intelligence-report/export",
        params={"format": "markdown"},
    )
    assert markdown.status_code == 200
    assert "Customer Intelligence Report" in markdown.text

    json_export = client.get(
        "/api/v1/customers/CUST-FINAL/intelligence-report/export",
        params={"format": "json"},
    )
    assert json_export.status_code == 200
    assert json_export.json()["customer_id"] == "CUST-FINAL"

    pdf = client.get(
        "/api/v1/customers/CUST-FINAL/intelligence-report/export",
        params={"format": "pdf"},
    )
    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF")


def _seed_final_customers(session: Session) -> None:
    session.add(
        DatasetMetadata(
            dataset_name="final_unit_test",
            source="unit",
            version="final-v1",
            rows=15,
            columns=["customer_id"],
            checksum="final-checksum",
            status="loaded",
        )
    )
    for index in range(5):
        low_customer_id = "CUST-FINAL" if index == 0 else f"CUST-LOW-{index}"
        session.add(
            Customer(
                customer_id=low_customer_id,
                full_name=f"Premium Customer {index}",
                gender="Female",
                age=44 + index,
                geography="Urban",
                education="Graduate",
                marital_status="Married",
                income_category="High",
                estimated_income=160000.0,
                credit_score=780,
                savings_balance=95000.0,
                tenure_months=72,
                source_dataset="final_unit_test",
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
                source_dataset="final_unit_test",
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
                source_dataset="final_unit_test",
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
                source_dataset="final_unit_test",
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
                source_dataset="final_unit_test",
                source_record_id=f"high-loan-{index}",
            )
        )
    session.add_all(
        [
            Product(
                customer_id="CUST-FINAL",
                product_type="Credit Card",
                status="active",
                credit_limit=200000.0,
                revolving_balance=15000.0,
                revenue=2400.0,
                source_dataset="final_unit_test",
                source_record_id="product-final-card",
            ),
            Transaction(
                customer_id="CUST-FINAL",
                step=1,
                transaction_type="CASH_IN",
                category="Cash Deposit",
                direction="credit",
                amount=160000.0,
                description="Salary Credit from HDFC Bank Mumbai",
                counterparty="HDFC Bank",
                is_fraud=0,
                source_dataset="final_unit_test",
                source_record_id="txn-final-1",
            ),
            Transaction(
                customer_id="CUST-FINAL",
                step=6,
                transaction_type="PAYMENT",
                category="Payments",
                direction="debit",
                amount=22000.0,
                description="Travel Booking business class flight",
                counterparty="Travel Desk",
                is_fraud=0,
                source_dataset="final_unit_test",
                source_record_id="txn-final-2",
            ),
            Transaction(
                customer_id="CUST-FINAL",
                step=8,
                transaction_type="PAYMENT",
                category="Payments",
                direction="debit",
                amount=9000.0,
                description="Amazon Purchase premium electronics",
                counterparty="Amazon",
                is_fraud=0,
                source_dataset="final_unit_test",
                source_record_id="txn-final-3",
            ),
        ]
    )
    session.commit()
