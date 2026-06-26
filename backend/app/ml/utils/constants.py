from __future__ import annotations

RISK_LABELS: tuple[str, str, str] = ("Low", "Medium", "High")

SEGMENT_LABELS: tuple[str, str, str, str, str] = (
    "Premium",
    "High Value",
    "Budget",
    "Young Investors",
    "Loan Focused",
)

ML_FEATURE_COLUMNS: tuple[str, ...] = (
    "credit_score",
    "estimated_income",
    "savings_balance",
    "age",
    "tenure_months",
    "debt_to_income",
    "savings_ratio",
    "spend_ratio",
    "credit_utilization",
    "salary_stability",
    "product_count",
    "loan_exposure",
    "average_transaction_amount",
    "transaction_frequency",
    "monthly_spending",
    "customer_tenure",
    "risk_indicators",
    "income_category_rank",
    "age_group_rank",
)

FEATURE_DESCRIPTIONS: dict[str, str] = {
    "credit_score": "Customer credit score from canonical profile.",
    "estimated_income": "Estimated annual income from canonical profile.",
    "savings_balance": "Savings or balance available for the customer.",
    "age": "Customer age.",
    "tenure_months": "Customer tenure in months.",
    "debt_to_income": "Total outstanding loan exposure divided by income.",
    "savings_ratio": "Savings or balance divided by income.",
    "spend_ratio": "Estimated monthly spend divided by income.",
    "credit_utilization": "Revolving credit balance divided by credit limit.",
    "salary_stability": "Heuristic stability score from tenure and income.",
    "product_count": "Number of active financial products.",
    "loan_exposure": "Total loan amount associated with the customer.",
    "average_transaction_amount": "Average amount across linked transactions.",
    "transaction_frequency": "Number of transactions linked to the customer.",
    "monthly_spending": "Estimated monthly debit spending.",
    "customer_tenure": "Customer tenure from the feature store.",
    "risk_indicators": "Count of deterministic financial risk flags.",
    "income_category_rank": "Numeric encoding of the income category.",
    "age_group_rank": "Numeric encoding of the customer age cohort.",
}

INCOME_CATEGORY_RANKS: dict[str, float] = {
    "Unknown": 0.0,
    "Low": 1.0,
    "Middle": 2.0,
    "Upper Middle": 3.0,
    "High": 4.0,
}

AGE_GROUP_RANKS: dict[str, float] = {
    "Unknown": 0.0,
    "Young Adult": 1.0,
    "Emerging": 2.0,
    "Established": 3.0,
    "Mature": 4.0,
    "Senior": 5.0,
}
