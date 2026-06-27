from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.db.session import SessionLocal, initialize_database  # noqa: E402
from app.models.canonical import Transaction  # noqa: E402
from app.nlp.services.intelligence import NLPIntelligenceService  # noqa: E402
from app.recommendation.service import RecommendationService  # noqa: E402


def main() -> None:
    initialize_database()
    with SessionLocal() as session:
        nlp_service = NLPIntelligenceService(session)
        nlp_status = nlp_service.process_all()
        customer_ids = list(
            session.scalars(
                select(Transaction.customer_id)
                .distinct()
                .order_by(Transaction.customer_id)
            )
        )
        recommendation_service = RecommendationService(
            session,
            use_model_predictions=False,
        )
        recommendation_service.seed_rules()
        generated_recommendations = 0
        for customer_id in customer_ids:
            recommendations = recommendation_service.generate_for_customer(
                customer_id,
                refresh_intelligence=False,
                ensure_rules=False,
            )
            generated_recommendations += len(recommendations)

        print("NLP status:", nlp_status)
        print("Customers processed:", len(customer_ids))
        print("Recommendations generated:", generated_recommendations)
        print("Recommendation status:", recommendation_service.status())


if __name__ == "__main__":
    main()
