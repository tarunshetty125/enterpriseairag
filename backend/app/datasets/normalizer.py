from __future__ import annotations

from app.datasets.types import NormalizedRow, RawRow
from app.datasets.utils import normalize_column_name


class DatasetNormalizer:
    """Normalizes CSV column names while preserving row values."""

    def normalize_rows(self, rows: list[RawRow]) -> list[NormalizedRow]:
        normalized_rows: list[NormalizedRow] = []
        for row in rows:
            normalized_rows.append(
                {normalize_column_name(key): value for key, value in row.items()}
            )
        return normalized_rows
