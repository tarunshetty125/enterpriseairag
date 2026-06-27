from __future__ import annotations

from app.feature_store.service import FeatureStoreService
from app.models.canonical import Customer, DatasetMetadata, Transaction
from app.nlp.services.intelligence import NLPIntelligenceService
from app.recommendation.service import RecommendationService
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_phase4_nlp_behaviour_and_recommendation_pipeline(
    client: TestClient,
    session: Session,
) -> None:
    _seed_phase4_customer(session)
    FeatureStoreService(session).generate_snapshots()

    nlp_service = NLPIntelligenceService(session)
    insights = nlp_service.transaction_insights("CUST-NLP")
    profile = nlp_service.behaviour_profile("CUST-NLP")

    assert len(insights) == 3
    assert {result.insight.category for result in insights} >= {"Salary", "Shopping"}
    assert "Regular Salary" in profile.flags
    assert "High Online Shopper" in profile.flags
    assert profile.summary

    recommendation_service = RecommendationService(
        session,
        use_model_predictions=False,
    )
    recommendations = recommendation_service.generate_for_customer(
        "CUST-NLP",
        refresh_intelligence=False,
    )

    assert recommendations
    assert recommendations[0].suitability_score >= 45
    assert recommendations[0].supporting_features
    assert recommendations[0].business_explanation

    insights_response = client.get("/api/v1/transactions/CUST-NLP/insights")
    assert insights_response.status_code == 200
    assert insights_response.json()["total"] == 3

    behaviour_response = client.get("/api/v1/customers/CUST-NLP/behaviour")
    assert behaviour_response.status_code == 200
    assert "Regular Salary" in behaviour_response.json()["flags"]

    generation_response = client.post("/api/v1/recommendations/generate/CUST-NLP")
    assert generation_response.status_code == 200
    assert generation_response.json()["generated"] > 0

    recommendation_response = client.get("/api/v1/recommendations/CUST-NLP")
    assert recommendation_response.status_code == 200
    assert recommendation_response.json()["recommendations"]

    rules_response = client.get("/api/v1/recommendation-rules")
    assert rules_response.status_code == 200
    assert len(rules_response.json()) >= 6

    status_response = client.get("/api/v1/intelligence/status")
    assert status_response.status_code == 200
    assert status_response.json()["transactionsProcessed"] == 3


def _seed_phase4_customer(session: Session) -> None:
    session.add(
        DatasetMetadata(
            dataset_name="phase4_unit_test",
            source="unit",
            version="phase4-v1",
            rows=1,
            columns=["customer_id"],
            checksum="phase4-checksum",
            status="loaded",
        )
    )
    session.add(
        Customer(
            customer_id="CUST-NLP",
            full_name="NLP Customer",
            gender="Female",
            age=34,
            geography="Urban",
            education="Graduate",
            marital_status="Single",
            income_category="High",
            estimated_income=120000.0,
            credit_score=760,
            savings_balance=70000.0,
            tenure_months=48,
            source_dataset="phase4_unit_test",
            source_record_id="customer-1",
            external_references={},
        )
    )
    session.add_all(
        [
            Transaction(
                customer_id="CUST-NLP",
                step=1,
                transaction_type="CASH_IN",
                category="Cash Deposit",
                direction="credit",
                amount=120000.0,
                description="Salary Credit from HDFC Bank Mumbai",
                counterparty="C100",
                is_fraud=0,
                source_dataset="phase4_unit_test",
                source_record_id="txn-1",
            ),
            Transaction(
                customer_id="CUST-NLP",
                step=6,
                transaction_type="PAYMENT",
                category="Payments",
                direction="debit",
                amount=4500.0,
                description="Amazon Purchase using credit card",
                counterparty="M100",
                is_fraud=0,
                source_dataset="phase4_unit_test",
                source_record_id="txn-2",
            ),
            Transaction(
                customer_id="CUST-NLP",
                step=13,
                transaction_type="PAYMENT",
                category="Payments",
                direction="debit",
                amount=2800.0,
                description="Flipkart shopping order",
                counterparty="M200",
                is_fraud=0,
                source_dataset="phase4_unit_test",
                source_record_id="txn-3",
            ),
        ]
    )
    session.commit()
