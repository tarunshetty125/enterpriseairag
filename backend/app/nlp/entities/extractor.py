from __future__ import annotations

import re
from typing import Any

from app.models.canonical import Transaction

BRAND_KEYWORDS = {
    "amazon": "Amazon",
    "fuel": "Fuel Merchant",
    "hospital": "Hospital",
    "restaurant": "Restaurant",
    "insurance": "Insurance Provider",
    "mutual": "Mutual Fund Provider",
}

LOCATION_KEYWORDS = {
    "mumbai": "Mumbai",
    "delhi": "Delhi",
    "bangalore": "Bangalore",
    "chennai": "Chennai",
    "pune": "Pune",
    "hyderabad": "Hyderabad",
}


class EntityExtractor:
    """Extracts normalized transaction entities from deterministic rules."""

    def extract(
        self,
        transaction: Transaction,
        normalized_description: str,
    ) -> dict[str, Any]:
        counterparty = transaction.counterparty or ""
        merchant = self._merchant(counterparty)
        institution = self._institution(counterparty)
        brand = self._keyword_lookup(normalized_description, BRAND_KEYWORDS)
        location = self._keyword_lookup(normalized_description, LOCATION_KEYWORDS)
        return {
            "merchant": merchant,
            "location": location,
            "payment_type": transaction.transaction_type.upper(),
            "institution": institution,
            "brand": brand,
            "counterparty": counterparty or None,
        }

    def _merchant(self, counterparty: str) -> str | None:
        if re.match(r"^M\d+", counterparty):
            return f"Merchant {counterparty}"
        return None

    def _institution(self, counterparty: str) -> str | None:
        if re.match(r"^C\d+", counterparty):
            return f"Institution {counterparty}"
        return None

    def _keyword_lookup(
        self,
        normalized_description: str,
        mapping: dict[str, str],
    ) -> str | None:
        for keyword, value in mapping.items():
            if keyword in normalized_description:
                return value
        return None
