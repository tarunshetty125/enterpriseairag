from __future__ import annotations

from collections import Counter, defaultdict
from time import perf_counter
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.feature_store.service import FeatureStoreService
from app.models.canonical import Customer, Transaction
from app.models.intelligence import BehaviourProfile, TransactionInsight
from app.nlp.pipelines.transaction_intelligence import NLP_PROCESSING_VERSION

BEHAVIOUR_PROFILE_VERSION = "behaviour_rules_v1"


class BehaviourProfileService:
    """Generates deterministic customer-level behaviour profiles."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def generate_profile(self, customer_id: str) -> BehaviourProfile:
        started = perf_counter()
        customer = self._customer(customer_id)
        if customer is None:
            msg = f"Customer not found: {customer_id}"
            raise ValueError(msg)
        insights = self._insights(customer_id)
        category_spend = self._category_spend(insights)
        category_counts = self._category_counts(insights)
        lifestyle = self._lifestyle_indicators(insights)
        features = self._behaviour_features(customer, insights, category_spend)
        flags = self._flags(customer, category_spend, category_counts, features)
        summary = self._summary(flags, category_spend, category_counts)
        profile_payload = {
            "customer_id": customer_id,
            "profile_version": BEHAVIOUR_PROFILE_VERSION,
            "summary": summary,
            "flags": flags,
            "lifestyle_indicators": lifestyle,
            "category_spend": category_spend,
            "category_counts": category_counts,
            "monthly_trends": self._monthly_trends(insights),
            "top_merchants": self._top_merchants(insights),
            "features": features,
            "processing_time_ms": round((perf_counter() - started) * 1000, 3),
        }
        existing = self.session.get(BehaviourProfile, customer_id)
        if existing is None:
            profile = BehaviourProfile(**profile_payload)
            self.session.add(profile)
        else:
            profile = existing
            for key, value in profile_payload.items():
                setattr(profile, key, value)
        self.session.commit()
        self.session.refresh(profile)
        return profile

    def get_profile(self, customer_id: str) -> BehaviourProfile | None:
        return self.session.get(BehaviourProfile, customer_id)

    def _customer(self, customer_id: str) -> Customer | None:
        return self.session.scalar(
            select(Customer)
            .where(Customer.customer_id == customer_id)
            .options(selectinload(Customer.loans), selectinload(Customer.products))
        )

    def _insights(self, customer_id: str) -> list[TransactionInsight]:
        return list(
            self.session.scalars(
                select(TransactionInsight)
                .where(TransactionInsight.customer_id == customer_id)
                .order_by(TransactionInsight.transaction_id)
            )
        )

    def _category_spend(
        self,
        insights: list[TransactionInsight],
    ) -> dict[str, float]:
        transactions = self._transactions_by_id(
            [insight.transaction_id for insight in insights]
        )
        spend: defaultdict[str, float] = defaultdict(float)
        for insight in insights:
            transaction = transactions.get(insight.transaction_id)
            if transaction is not None and transaction.direction == "debit":
                spend[insight.category] += transaction.amount
        return {
            category: round(amount, 2) for category, amount in sorted(spend.items())
        }

    def _category_counts(
        self,
        insights: list[TransactionInsight],
    ) -> dict[str, int]:
        counts = Counter(insight.category for insight in insights)
        return dict(sorted(counts.items()))

    def _lifestyle_indicators(
        self,
        insights: list[TransactionInsight],
    ) -> list[str]:
        counter: Counter[str] = Counter()
        for insight in insights:
            counter.update(str(item) for item in insight.lifestyle_indicators)
        return [name for name, _ in counter.most_common(12)]

    def _behaviour_features(
        self,
        customer: Customer,
        insights: list[TransactionInsight],
        category_spend: dict[str, float],
    ) -> dict[str, Any]:
        transactions = self._transactions_by_id(
            [insight.transaction_id for insight in insights]
        )
        debit_total = round(sum(category_spend.values()), 2)
        credit_total = round(
            sum(
                transaction.amount
                for transaction in transactions.values()
                if transaction.direction == "credit"
            ),
            2,
        )
        snapshot = FeatureStoreService(self.session).latest_for_customer(
            customer.customer_id
        )
        feature_values = (
            snapshot.features.get("values", {})
            if snapshot is not None and isinstance(snapshot.features, dict)
            else {}
        )
        return {
            "transaction_count": len(insights),
            "debit_total": debit_total,
            "credit_total": credit_total,
            "average_transaction_amount": (
                round(
                    sum(transaction.amount for transaction in transactions.values())
                    / len(transactions),
                    2,
                )
                if transactions
                else 0.0
            ),
            "largest_transaction": round(
                max(
                    (transaction.amount for transaction in transactions.values()),
                    default=0.0,
                ),
                2,
            ),
            "salary_credit_count": sum(
                1 for insight in insights if insight.category == "Salary"
            ),
            "weekend_transaction_ratio": self._weekend_ratio(transactions.values()),
            "debt_to_income": self._numeric(feature_values.get("debt_to_income")),
            "savings_ratio": self._numeric(feature_values.get("savings_ratio")),
            "product_count": self._numeric(feature_values.get("product_count")),
            "nlp_processing_version": NLP_PROCESSING_VERSION,
        }

    def _flags(
        self,
        customer: Customer,
        category_spend: dict[str, float],
        category_counts: dict[str, int],
        features: dict[str, Any],
    ) -> list[str]:
        flags: list[str] = []
        debit_total = float(features["debit_total"])
        transaction_count = int(features["transaction_count"])

        def spend_share(category: str) -> float:
            if debit_total <= 0:
                return 0.0
            return category_spend.get(category, 0.0) / debit_total

        if category_counts.get("Shopping", 0) >= 2 or spend_share("Shopping") >= 0.25:
            flags.append("High Online Shopper")
        if category_counts.get("Travel", 0) >= 2 or spend_share("Travel") >= 0.25:
            flags.append("Frequent Traveller")
        if float(features["largest_transaction"]) >= 100000:
            flags.append("Luxury Spending")
        if category_counts.get("Medical", 0) >= 2 or spend_share("Medical") >= 0.2:
            flags.append("Medical Heavy")
        if category_counts.get("ATM", 0) >= max(1, transaction_count * 0.35):
            flags.append("Cash Dominant")
        if category_counts.get("Investment", 0) > 0:
            flags.append("Investment Focused")
        if int(features["salary_credit_count"]) > 0:
            flags.append("Regular Salary")
        if float(features["debt_to_income"]) >= 1.5 or category_counts.get("Loan", 0):
            flags.append("High EMI Burden")
        if float(features["weekend_transaction_ratio"]) >= 0.4:
            flags.append("Weekend Spender")
        if (
            int(features["salary_credit_count"]) == 0
            and customer.estimated_income is None
        ):
            flags.append("Irregular Income")
        return flags or ["Low Activity"]

    def _summary(
        self,
        flags: list[str],
        category_spend: dict[str, float],
        category_counts: dict[str, int],
    ) -> str:
        if not category_counts:
            return "This customer has no linked transactions for behavioural analysis."
        top_category = max(category_counts, key=lambda name: category_counts[name])
        if "Regular Salary" in flags and len(flags) > 1:
            other_flags = ", ".join(
                flag.lower() for flag in flags if flag != "Regular Salary"
            )
            return (
                "This customer receives regular income and shows "
                f"{other_flags}. "
                f"The most frequent transaction category is {top_category.lower()}."
            )
        return (
            f"This customer is primarily associated with {top_category.lower()} "
            f"activity and shows {', '.join(flag.lower() for flag in flags)}."
        )

    def _monthly_trends(
        self,
        insights: list[TransactionInsight],
    ) -> list[dict[str, Any]]:
        transactions = self._transactions_by_id(
            [insight.transaction_id for insight in insights]
        )
        trends: dict[int, dict[str, Any]] = {}
        for insight in insights:
            transaction = transactions.get(insight.transaction_id)
            if transaction is None:
                continue
            period = ((transaction.step or 1) - 1) // 30 + 1
            row = trends.setdefault(
                period,
                {"period": f"Month {period}", "credit": 0.0, "debit": 0.0, "count": 0},
            )
            row[str(transaction.direction)] += round(transaction.amount, 2)
            row["count"] += 1
        return [
            {
                **row,
                "credit": round(float(row["credit"]), 2),
                "debit": round(float(row["debit"]), 2),
            }
            for _, row in sorted(trends.items())
        ]

    def _top_merchants(
        self,
        insights: list[TransactionInsight],
    ) -> list[dict[str, Any]]:
        transactions = self._transactions_by_id(
            [insight.transaction_id for insight in insights]
        )
        totals: defaultdict[str, float] = defaultdict(float)
        counts: Counter[str] = Counter()
        for insight in insights:
            transaction = transactions.get(insight.transaction_id)
            if transaction is None:
                continue
            entities = insight.entities if isinstance(insight.entities, dict) else {}
            merchant = (
                entities.get("merchant")
                or entities.get("institution")
                or entities.get("counterparty")
                or "Unknown"
            )
            merchant_name = str(merchant)
            totals[merchant_name] += transaction.amount
            counts[merchant_name] += 1
        return [
            {"name": name, "amount": round(totals[name], 2), "count": counts[name]}
            for name, _ in counts.most_common(5)
        ]

    def _weekend_ratio(self, transactions: Any) -> float:
        values = list(transactions)
        if not values:
            return 0.0
        weekend_count = sum(
            1 for transaction in values if (transaction.step or 1) % 7 in {0, 6}
        )
        return round(weekend_count / len(values), 4)

    def _transactions_by_id(self, transaction_ids: list[int]) -> dict[int, Transaction]:
        if not transaction_ids:
            return {}
        transactions = self.session.scalars(
            select(Transaction).where(Transaction.id.in_(transaction_ids))
        )
        return {transaction.id: transaction for transaction in transactions}

    def _numeric(self, value: Any) -> float:
        if isinstance(value, int | float):
            return float(value)
        return 0.0
