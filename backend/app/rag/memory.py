from __future__ import annotations

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai import ChatMessage, ChatSession


class ConversationMemoryService:
    """SQLite-backed lightweight conversation memory."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_or_create(
        self,
        *,
        session_id: str | None,
        title: str,
        provider: str,
        model: str,
    ) -> ChatSession:
        if session_id:
            existing = self.session.get(ChatSession, session_id)
            if existing is not None:
                return existing
        chat_session = ChatSession(
            session_id=session_id or uuid4().hex,
            title=title[:200],
            provider=provider,
            model=model,
        )
        self.session.add(chat_session)
        self.session.commit()
        return chat_session

    def add_message(
        self,
        *,
        session_id: str,
        role: str,
        content: str,
        retrieved_context: list[dict[str, object]] | None = None,
        citations: list[dict[str, object]] | None = None,
        provider: str | None = None,
        model: str | None = None,
        latency_ms: float | None = None,
        token_usage: dict[str, object] | None = None,
    ) -> ChatMessage:
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            retrieved_context=retrieved_context or [],
            citations=citations or [],
            provider=provider,
            model=model,
            latency_ms=latency_ms,
            token_usage=token_usage or {},
        )
        self.session.add(message)
        self.session.commit()
        return message

    def history(self, session_id: str, limit: int = 12) -> list[ChatMessage]:
        return list(
            self.session.scalars(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.desc())
                .limit(limit)
            )
        )[::-1]

    def sessions(self) -> list[ChatSession]:
        return list(
            self.session.scalars(
                select(ChatSession).order_by(ChatSession.updated_at.desc())
            )
        )
