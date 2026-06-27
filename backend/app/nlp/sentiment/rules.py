from __future__ import annotations

from dataclasses import dataclass

from app.models.canonical import Transaction

POSITIVE_TERMS = {
    "cash in",
    "credit",
    "deposit",
    "income",
    "investment",
    "salary",
}

NEGATIVE_TERMS = {
    "atm",
    "cash out",
    "debit",
    "emi",
    "fraud",
    "hospital",
    "loan",
    "medical",
}


@dataclass(frozen=True)
class SentimentResult:
    label: str
    score: float


class SentimentAnalyzer:
    """Lightweight deterministic sentiment for financial transaction text."""

    def analyze(
        self,
        transaction: Transaction,
        normalized_description: str,
        category: str,
    ) -> SentimentResult:
        text = f"{normalized_description} {transaction.direction} {category.lower()}"
        score = 0.0
        score += sum(0.35 for term in POSITIVE_TERMS if term in text)
        score -= sum(0.35 for term in NEGATIVE_TERMS if term in text)

        if transaction.direction == "credit":
            score += 0.2
        if transaction.is_fraud:
            score -= 1.0
        if category in {"Salary", "Investment"}:
            score += 0.25
        if category in {"ATM", "Medical", "Loan"}:
            score -= 0.25

        score = max(-1.0, min(1.0, round(score, 3)))
        if score >= 0.25:
            return SentimentResult(label="positive", score=score)
        if score <= -0.25:
            return SentimentResult(label="negative", score=score)
        return SentimentResult(label="neutral", score=score)
