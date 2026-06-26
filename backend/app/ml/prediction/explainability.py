from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FeatureContribution:
    name: str
    value: float | str | None
    importance: float
    description: str


class ExplainabilityEngine:
    """Creates factual explanations from model feature importance and values."""

    def summarize(
        self,
        *,
        prediction: str,
        contributions: list[FeatureContribution],
    ) -> str:
        if not contributions:
            return f"The model predicted {prediction} risk without feature detail."
        phrases = [self._phrase(contribution) for contribution in contributions[:3]]
        joined = ", ".join(phrases)
        return (
            f"The model predicted {prediction} risk because the highest-weighted "
            f"features for this customer were {joined}."
        )

    def _phrase(self, contribution: FeatureContribution) -> str:
        direction = self._direction(contribution.name, contribution.value)
        if direction:
            return f"{direction} {contribution.name.replace('_', ' ')}"
        return f"{contribution.name.replace('_', ' ')} " f"(value {contribution.value})"

    def _direction(self, name: str, value: float | str | None) -> str | None:
        if not isinstance(value, int | float):
            return None
        if name in {"debt_to_income", "credit_utilization", "spend_ratio"}:
            if value >= 0.75:
                return "high"
            if value <= 0.1:
                return "low"
        if name in {"loan_exposure", "monthly_spending"}:
            if value >= 100000:
                return "high"
            if value <= 1000:
                return "low"
        if name in {"savings_ratio", "salary_stability"}:
            if value >= 0.75:
                return "high"
            if value <= 0.1:
                return "low"
        if name == "credit_score":
            if value >= 720:
                return "strong"
            if value < 620:
                return "low"
        if name == "risk_indicators":
            if value >= 2:
                return "elevated"
            if value == 0:
                return "low"
        return None
