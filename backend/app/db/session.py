from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.base import Base
from app.models import (
    canonical,  # noqa: F401
    intelligence,  # noqa: F401
    ml,  # noqa: F401
)

settings = get_settings()
settings.database.sqlite_path.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    settings.database.sqlalchemy_url,
    echo=settings.database.echo,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def initialize_database() -> None:
    settings.database.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


def get_db_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
