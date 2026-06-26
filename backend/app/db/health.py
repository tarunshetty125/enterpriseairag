from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine


@dataclass(frozen=True)
class DatabaseHealth:
    status: str
    details: str


def check_database_health() -> DatabaseHealth:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return DatabaseHealth(status="ok", details="SQLite connection verified")
    except SQLAlchemyError as exc:
        return DatabaseHealth(status="error", details=str(exc))
