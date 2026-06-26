from __future__ import annotations

from app.datasets.catalog import DatasetDefinition
from app.datasets.types import RawRow, ValidationIssue, ValidationResult


class DatasetValidator:
    """Validates raw dataset structure before normalization."""

    def validate(
        self,
        definition: DatasetDefinition,
        rows: list[RawRow],
        columns: list[str],
    ) -> ValidationResult:
        column_set = set(columns)
        missing_columns = [
            column for column in definition.required_columns if column not in column_set
        ]
        issues: list[ValidationIssue] = []

        if not rows:
            issues.append(
                ValidationIssue(column="*", message="Dataset contains no rows")
            )

        return ValidationResult(
            is_valid=not missing_columns and not issues,
            missing_columns=missing_columns,
            issues=issues,
        )
