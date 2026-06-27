from __future__ import annotations

from dataclasses import dataclass
from typing import Any

RECOMMENDATION_RULE_VERSION = "recommendation_rules_v1"


@dataclass(frozen=True)
class ProductRule:
    rule_id: str
    product_name: str
    description: str
    base_score: float
    conditions: dict[str, Any]


PRODUCT_RULES: tuple[ProductRule, ...] = (
    ProductRule(
        rule_id="premium_credit_card",
        product_name="Credit Card",
        description=(
            "Premium card for low-risk customers with travel or shopping behaviour."
        ),
        base_score=45.0,
        conditions={
            "risk_levels": ["Low", "Medium"],
            "positive_flags": ["Frequent Traveller", "High Online Shopper"],
            "min_income": 80000,
        },
    ),
    ProductRule(
        rule_id="home_loan",
        product_name="Home Loan",
        description="Home loan for stable-income customers with low debt pressure.",
        base_score=42.0,
        conditions={
            "risk_levels": ["Low", "Medium"],
            "required_flags": ["Regular Salary"],
            "max_debt_to_income": 1.5,
            "min_income": 60000,
        },
    ),
    ProductRule(
        rule_id="personal_loan",
        product_name="Personal Loan",
        description="Personal loan for medium-value customers with manageable risk.",
        base_score=34.0,
        conditions={
            "risk_levels": ["Low", "Medium"],
            "max_debt_to_income": 2.5,
            "min_income": 40000,
        },
    ),
    ProductRule(
        rule_id="fixed_deposit",
        product_name="Fixed Deposit",
        description="Deposit product for customers with surplus savings.",
        base_score=38.0,
        conditions={
            "risk_levels": ["Low", "Medium", "High"],
            "min_savings_ratio": 0.35,
            "min_savings_balance": 20000,
        },
    ),
    ProductRule(
        rule_id="mutual_fund",
        product_name="Mutual Fund",
        description=(
            "Market-linked investment for high-value or investment-focused customers."
        ),
        base_score=40.0,
        conditions={
            "risk_levels": ["Low", "Medium"],
            "positive_flags": ["Investment Focused", "Regular Salary"],
            "min_income": 70000,
        },
    ),
    ProductRule(
        rule_id="sip",
        product_name="SIP",
        description="Systematic investment plan for regular-income customers.",
        base_score=42.0,
        conditions={
            "risk_levels": ["Low", "Medium"],
            "required_flags": ["Regular Salary"],
            "min_income": 40000,
        },
    ),
    ProductRule(
        rule_id="insurance",
        product_name="Insurance",
        description=(
            "Protection product for customers with health, age, or family risk signals."
        ),
        base_score=35.0,
        conditions={
            "positive_flags": ["Medical Heavy"],
            "min_age": 40,
        },
    ),
    ProductRule(
        rule_id="savings_upgrade",
        product_name="Savings Account Upgrade",
        description="Account upgrade for customers with strong balances or income.",
        base_score=36.0,
        conditions={
            "min_income": 80000,
            "min_savings_balance": 30000,
        },
    ),
)
