from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.models.ai import ChatSession
from app.rag.service import RAGService
from app.schemas.ai import (
    ChatRequest,
    ChatResponse,
    ChatSessionDetailResponse,
    ChatSessionResponse,
    CitationResponse,
    TokenUsageResponse,
)

router = APIRouter(tags=["chat"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, session: DbSession) -> ChatResponse:
    result = RAGService(session).chat(
        question=request.message,
        session_id=request.session_id,
        customer_id=request.customer_id,
    )
    return ChatResponse(
        session_id=result.session_id,
        answer=result.answer,
        citations=[
            CitationResponse(
                document=citation.document,
                section=citation.section,
                chunk=citation.chunk,
                similarity_score=citation.similarity_score,
            )
            for citation in result.citations
        ],
        provider=result.provider,
        model=result.model,
        latency_ms=result.latency_ms,
        token_usage=TokenUsageResponse(
            prompt_tokens=result.token_usage.prompt_tokens,
            completion_tokens=result.token_usage.completion_tokens,
            total_tokens=result.token_usage.total_tokens,
        ),
        retrieved_chunks=result.retrieved_chunks,
        context_size=result.context_size,
        prompt_version=result.prompt_version,
        status=result.status,
    )


@router.get("/chat/sessions", response_model=list[ChatSessionResponse])
def chat_sessions(session: DbSession) -> list[ChatSessionResponse]:
    return [
        ChatSessionResponse(
            session_id=row.session_id,
            title=row.title,
            provider=row.provider,
            model=row.model,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
        for row in RAGService(session).sessions()
    ]


@router.get("/chat/{session_id}", response_model=ChatSessionDetailResponse)
def chat_session(session_id: str, session: DbSession) -> ChatSessionDetailResponse:
    row = session.get(ChatSession, session_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return ChatSessionDetailResponse(
        session=ChatSessionResponse(
            session_id=row.session_id,
            title=row.title,
            provider=row.provider,
            model=row.model,
            created_at=row.created_at,
            updated_at=row.updated_at,
        ),
        messages=RAGService(session).session_messages(session_id),
    )
