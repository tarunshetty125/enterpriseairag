from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


class RetryPolicy:
    """Small deterministic retry wrapper for provider calls."""

    def __init__(self, attempts: int = 2) -> None:
        self.attempts = attempts

    def run(self, operation: Callable[[], T]) -> T:
        last_error: Exception | None = None
        for _ in range(self.attempts):
            try:
                return operation()
            except Exception as exc:
                last_error = exc
        if last_error is not None:
            raise last_error
        return operation()
