from __future__ import annotations

from app.models.canonical import Transaction


class LifestyleIndicatorExtractor:
    """Maps classified transactions into deterministic lifestyle indicators."""

    def extract(self, transaction: Transaction, category: str) -> list[str]:
        indicators: list[str] = []
        mapping = {
            "Salary": "Regular Income",
            "Shopping": "Online Shopping",
            "Food": "Dining Activity",
            "Travel": "Travel Activity",
            "Fuel": "Commute Activity",
            "Medical": "Healthcare Spend",
            "ATM": "Cash Usage",
            "Bills": "Recurring Payments",
            "Investment": "Investment Activity",
            "Insurance": "Protection Need",
            "Entertainment": "Entertainment Spend",
            "Education": "Education Spend",
            "Loan": "Debt Obligation",
            "Transfer": "Money Movement",
        }
        indicator = mapping.get(category)
        if indicator:
            indicators.append(indicator)
        if transaction.amount >= 100000:
            indicators.append("High Value Transaction")
        if transaction.direction == "credit":
            indicators.append("Income Credit")
        if transaction.is_fraud:
            indicators.append("Fraud Signal")
        return list(dict.fromkeys(indicators))
