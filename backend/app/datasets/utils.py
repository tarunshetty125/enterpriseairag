from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable
from decimal import Decimal, InvalidOperation


def stable_hash(value: str, length: int = 16) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def build_customer_id(namespace: str, source_record_id: str) -> str:
    return f"CUST-{stable_hash(f'{namespace}|{source_record_id}', 12).upper()}"


def normalize_column_name(value: str) -> str:
    value = value.strip().replace("-", "_").replace(" ", "_")
    value = re.sub(r"(?<!^)(?=[A-Z])", "_", value)
    return re.sub(r"_+", "_", value).strip("_").lower()


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    if not stripped or stripped.lower() in {"nan", "none", "null", "unknown"}:
        return None
    return stripped


def to_float(value: str | int | float | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, int | float):
        return float(value)
    cleaned = value.strip().replace(",", "")
    if cleaned == "":
        return None
    try:
        return float(Decimal(cleaned))
    except InvalidOperation:
        return None


def to_int(value: str | int | float | None) -> int | None:
    numeric = to_float(value)
    if numeric is None:
        return None
    return int(round(numeric))


def checksum_lines(lines: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for line in lines:
        digest.update(line.encode("utf-8"))
    return digest.hexdigest()


def income_category(value: float | None) -> str:
    if value is None:
        return "Unknown"
    if value < 40000:
        return "Low"
    if value < 90000:
        return "Middle"
    if value < 150000:
        return "Upper Middle"
    return "High"


def age_group(age: int | None) -> str:
    if age is None:
        return "Unknown"
    if age < 30:
        return "Young Adult"
    if age < 45:
        return "Established"
    if age < 60:
        return "Mature"
    return "Senior"
