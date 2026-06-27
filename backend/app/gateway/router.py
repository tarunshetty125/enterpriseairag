from __future__ import annotations

from sqlalchemy.orm import Session

from app.providers.base import AIProvider
from app.providers.manager import ProviderManager


class RequestRouter:
    """Selects the active provider for gateway calls."""

    def __init__(self, session: Session) -> None:
        self.manager = ProviderManager(session)

    def active_provider(self) -> AIProvider:
        return self.manager.active_provider()
