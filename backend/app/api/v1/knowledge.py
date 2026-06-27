"""Knowledge Base API routes.

Policy document ingestion, document listing, and RAG index status.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.rag.service import RAGService
from app.schemas.ai import (
    KnowledgeDocumentResponse,
    KnowledgeIngestResponse,
    KnowledgeStatusResponse,
)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.post("/ingest", response_model=KnowledgeIngestResponse)
def ingest_knowledge(session: DbSession) -> KnowledgeIngestResponse:
    result = RAGService(session).ingest()
    return KnowledgeIngestResponse(
        documents_indexed=int(result["documents_indexed"]),
        chunks_indexed=int(result["chunks_indexed"]),
        embedding_backend=str(result["embedding_backend"]),
        vector_backend=str(result["vector_backend"]),
    )


@router.get("/documents", response_model=list[KnowledgeDocumentResponse])
def knowledge_documents(session: DbSession) -> list[KnowledgeDocumentResponse]:
    return [
        KnowledgeDocumentResponse(
            id=document.id,
            document_name=document.document_name,
            document_type=document.document_type,
            source_path=document.source_path,
            version=document.version,
            checksum=document.checksum,
            status=document.status,
            chunk_count=document.chunk_count,
            indexed_at=document.indexed_at,
        )
        for document in RAGService(session).documents()
    ]


@router.get("/status", response_model=KnowledgeStatusResponse)
def knowledge_status(session: DbSession) -> KnowledgeStatusResponse:
    return KnowledgeStatusResponse(**RAGService(session).status())
