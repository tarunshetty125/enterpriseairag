from __future__ import annotations

from dataclasses import dataclass

from app.models.canonical import Transaction

TRANSACTION_CATEGORIES: tuple[str, ...] = (
    "Salary",
    "Shopping",
    "Food",
    "Travel",
    "Fuel",
    "Medical",
    "ATM",
    "Bills",
    "Investment",
    "Insurance",
    "Entertainment",
    "Education",
    "Loan",
    "Transfer",
    "Miscellaneous",
)

KEYWORD_CATEGORY_RULES: dict[str, str] = {
    "salary": "Salary",
    "payroll": "Salary",
    "amazon": "Shopping",
    "shopping": "Shopping",
    "restaurant": "Food",
    "food": "Food",
    "travel": "Travel",
    "booking": "Travel",
    "fuel": "Fuel",
    "hospital": "Medical",
    "medical": "Medical",
    "atm": "ATM",
    "cash out": "ATM",
    "bill": "Bills",
    "utility": "Bills",
    "investment": "Investment",
    "mutual": "Investment",
    "insurance": "Insurance",
    "movie": "Entertainment",
    "education": "Education",
    "tuition": "Education",
    "loan": "Loan",
    "transfer": "Transfer",
}


@dataclass(frozen=True)
class ClassificationResult:
    category: str
    reason: str


class TransactionClassifier:
    """Rule-assisted financial transaction classification."""

    def classify(
        self,
        transaction: Transaction,
        normalized_description: str,
    ) -> ClassificationResult:
        text = f"{normalized_description} {transaction.category.lower()}"
        for keyword, category in KEYWORD_CATEGORY_RULES.items():
            if keyword in text:
                return ClassificationResult(
                    category=category,
                    reason=f"Matched keyword rule: {keyword}",
                )

        transaction_type = transaction.transaction_type.upper()
        if transaction_type == "CASH_IN":
            return ClassificationResult(
                category="Salary",
                reason="CASH_IN credit is treated as income-like salary activity.",
            )
        if transaction_type == "CASH_OUT":
            return ClassificationResult(
                category="ATM",
                reason="CASH_OUT maps to cash withdrawal behaviour.",
            )
        if transaction_type == "TRANSFER":
            return ClassificationResult(
                category="Transfer",
                reason="TRANSFER maps to money movement.",
            )
        if transaction_type == "DEBIT":
            return ClassificationResult(
                category="Bills",
                reason="DEBIT maps to recurring payment or bill behaviour.",
            )
        if transaction_type == "PAYMENT":
            return self._payment_category(transaction.amount)

        return ClassificationResult(
            category="Miscellaneous",
            reason="No specific keyword or transaction-type rule matched.",
        )

    def _payment_category(self, amount: float) -> ClassificationResult:
        if amount >= 15000:
            return ClassificationResult(
                category="Travel",
                reason="High-value payment amount band maps to travel.",
            )
        if amount >= 8000:
            return ClassificationResult(
                category="Shopping",
                reason="Mid-high payment amount band maps to shopping.",
            )
        if amount >= 3000:
            return ClassificationResult(
                category="Bills",
                reason="Mid payment amount band maps to bills.",
            )
        if amount >= 1000:
            return ClassificationResult(
                category="Food",
                reason="Low-mid payment amount band maps to dining or food.",
            )
        return ClassificationResult(
            category="Entertainment",
            reason="Small payment amount band maps to entertainment.",
        )
