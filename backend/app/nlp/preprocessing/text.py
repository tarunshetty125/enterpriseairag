from __future__ import annotations

import re

STOP_WORDS = {
    "a",
    "an",
    "and",
    "at",
    "for",
    "from",
    "in",
    "of",
    "on",
    "paysim",
    "the",
    "to",
    "transaction",
}


class TransactionTextPreprocessor:
    """Deterministic text cleaning and keyword extraction."""

    def clean(self, value: str | None) -> str:
        text = (value or "").strip()
        text = text.replace("_", " ")
        return re.sub(r"\s+", " ", text)

    def normalize(self, value: str | None) -> str:
        cleaned = self.clean(value).lower()
        return re.sub(r"[^a-z0-9\s]", "", cleaned)

    def keywords(self, text: str, *extra_values: str | None) -> list[str]:
        tokens = re.findall(
            r"[a-z0-9]+",
            self.normalize(" ".join([text, *[v or "" for v in extra_values]])),
        )
        keywords = [
            token
            for token in tokens
            if token not in STOP_WORDS and not token.isdigit() and len(token) > 1
        ]
        return list(dict.fromkeys(keywords))[:12]
