from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.gateway.ai_gateway import AIGateway, GatewayRequest
from app.intelligence.context_builder import ContextBuilder, ContextChunk
from app.models.ai import ChatSession, KnowledgeChunk, KnowledgeDocument
from app.prompts.manager import PromptManager
from app.providers.base import ProviderConfigurationError, ProviderMessage, TokenUsage
from app.providers.manager import ProviderManager
from app.rag.embeddings import EmbeddingManager
from app.rag.memory import ConversationMemoryService
from app.rag.policy_loader import PolicyLoader
from app.rag.splitter import RecursiveTextSplitter
from app.rag.vectorstore import VectorRecord, VectorSearchResult, VectorStore


@dataclass(frozen=True)
class Citation:
    document: str
    section: str
    chunk: int
    similarity_score: float


@dataclass(frozen=True)
class RetrievalResult:
    chunk: KnowledgeChunk
    score: float


@dataclass(frozen=True)
class ChatResult:
    session_id: str
    answer: str
    citations: list[Citation]
    provider: str
    model: str
    latency_ms: float
    token_usage: TokenUsage
    retrieved_chunks: int
    context_size: int
    prompt_version: str
    status: str


class RAGService:
    """Policy RAG orchestration with grounded citations."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.settings = get_settings()
        provider_settings = ProviderManager(session).current_settings()
        self.embedding_manager = EmbeddingManager(provider_settings.embedding_model)
        self.vectorstore = VectorStore(self.settings.ai.vectorstore_path)

    def ingest(self) -> dict[str, int | str]:
        provider_settings = ProviderManager(self.session).current_settings()
        loader = PolicyLoader(self.settings.data.policies_path)
        splitter = RecursiveTextSplitter(provider_settings.chunk_size)
        documents = loader.load()
        self.session.execute(delete(KnowledgeChunk))
        self.session.execute(delete(KnowledgeDocument))
        vector_records: list[VectorRecord] = []
        for document in documents:
            row = KnowledgeDocument(
                document_name=document.name,
                document_type=document.document_type,
                source_path=document.source_path.as_posix(),
                version=document.version,
                checksum=document.checksum,
                status="indexed",
                chunk_count=0,
            )
            self.session.add(row)
            self.session.flush()
            chunks = splitter.split(document.text)
            row.chunk_count = len(chunks)
            for chunk in chunks:
                embedding = self.embedding_manager.embed(chunk.content)
                chunk_row = KnowledgeChunk(
                    document_id=row.id,
                    document_name=row.document_name,
                    chunk_index=chunk.chunk_index,
                    section=chunk.section,
                    content=chunk.content,
                    token_count=chunk.token_count,
                    embedding_metadata=embedding.metadata,
                )
                self.session.add(chunk_row)
                self.session.flush()
                vector_records.append(
                    VectorRecord(
                        chunk_id=chunk_row.id,
                        document=row.document_name,
                        section=chunk.section,
                        content=chunk.content,
                        vector=embedding.vector,
                        metadata=embedding.metadata,
                    )
                )
        self.vectorstore.build(vector_records)
        self.session.commit()
        return {
            "documents_indexed": len(documents),
            "chunks_indexed": len(vector_records),
            "embedding_backend": self.embedding_manager.backend,
            "vector_backend": self.vectorstore.backend,
        }

    def documents(self) -> list[KnowledgeDocument]:
        return list(
            self.session.scalars(
                select(KnowledgeDocument).order_by(KnowledgeDocument.document_name)
            )
        )

    def status(self) -> dict[str, Any]:
        latest = self.session.scalar(
            select(KnowledgeDocument)
            .order_by(KnowledgeDocument.indexed_at.desc())
            .limit(1)
        )
        stats = self.vectorstore.stats()
        return {
            "document_count": self.session.scalar(
                select(func.count(KnowledgeDocument.id))
            )
            or 0,
            "chunk_count": self.session.scalar(select(func.count(KnowledgeChunk.id)))
            or 0,
            "embedding_model": ProviderManager(self.session)
            .current_settings()
            .embedding_model,
            "embedding_backend": self.embedding_manager.backend,
            "vector_backend": stats["backend"],
            "faiss_index_size": stats["index_size"],
            "dimensions": stats["dimensions"],
            "latest_indexed_at": latest.indexed_at if latest else None,
        }

    def retrieve(self, question: str) -> list[RetrievalResult]:
        provider_settings = ProviderManager(self.session).current_settings()
        embedding = self.embedding_manager.embed(question)
        results = self.vectorstore.search(
            embedding.vector,
            top_k=provider_settings.retrieval_top_k,
        )
        filtered = [
            result
            for result in results
            if result.similarity_score >= provider_settings.similarity_threshold
        ]
        return [self._retrieval_result(result) for result in filtered]

    def chat(
        self,
        *,
        question: str,
        session_id: str | None = None,
        customer_id: str | None = None,
    ) -> ChatResult:
        provider_manager = ProviderManager(self.session)
        settings = provider_manager.current_settings()
        memory = ConversationMemoryService(self.session)
        chat_session = memory.get_or_create(
            session_id=session_id,
            title=question,
            provider=settings.provider,
            model=settings.model,
        )
        retrieved = self.retrieve(question)
        citations = [self._citation(item) for item in retrieved]
        context_chunks = [
            ContextChunk(
                document=item.chunk.document_name,
                section=item.chunk.section,
                chunk_id=item.chunk.id,
                similarity_score=item.score,
                content=item.chunk.content,
            )
            for item in retrieved
        ]
        history = [
            {"role": message.role, "content": message.content}
            for message in memory.history(chat_session.session_id)
        ]
        structured_context = ContextBuilder(self.session).build(
            customer_id=customer_id,
            conversation_history=history,
            retrieved_chunks=context_chunks,
        )
        context_text = self._context_text(context_chunks)
        citation_text = self._citation_text(citations)
        if not retrieved:
            answer = "Insufficient supporting documentation."
            usage = TokenUsage()
            latency = 0.0
            status = "insufficient_evidence"
            prompt_version = "not_rendered"
        else:
            prompt, template = PromptManager().render(
                "rag_chat",
                {
                    "question": question,
                    "context": context_text,
                    "citations": citation_text,
                },
            )
            prompt_version = template.version
            try:
                gateway_response = AIGateway(self.session).chat(
                    GatewayRequest(
                        messages=[
                            ProviderMessage(role="system", content=prompt),
                            ProviderMessage(role="user", content=question),
                        ],
                        operation="rag_chat",
                        metadata={
                            "prompt": template.name,
                            "prompt_version": template.version,
                        },
                        retrieved_chunks=len(retrieved),
                        context_size=len(str(structured_context.to_dict())),
                    )
                )
                answer = gateway_response.content
                usage = gateway_response.usage
                latency = gateway_response.latency_ms
                status = "success"
            except ProviderConfigurationError:
                answer = self._extractive_answer(question, retrieved)
                usage = TokenUsage()
                latency = 0.0
                status = "provider_not_configured"
        citation_payload = [citation.__dict__ for citation in citations]
        context_payload = [
            {
                "document": chunk.document,
                "section": chunk.section,
                "chunk": chunk.chunk_id,
                "similarity_score": chunk.similarity_score,
            }
            for chunk in context_chunks
        ]
        memory.add_message(
            session_id=chat_session.session_id,
            role="user",
            content=question,
        )
        memory.add_message(
            session_id=chat_session.session_id,
            role="assistant",
            content=answer,
            retrieved_context=context_payload,
            citations=citation_payload,
            provider=settings.provider,
            model=settings.model,
            latency_ms=latency,
            token_usage={
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
            },
        )
        return ChatResult(
            session_id=chat_session.session_id,
            answer=answer,
            citations=citations,
            provider=settings.provider,
            model=settings.model,
            latency_ms=latency,
            token_usage=usage,
            retrieved_chunks=len(retrieved),
            context_size=len(str(structured_context.to_dict())),
            prompt_version=prompt_version,
            status=status,
        )

    def sessions(self) -> list[ChatSession]:
        return ConversationMemoryService(self.session).sessions()

    def session_messages(self, session_id: str) -> list[dict[str, Any]]:
        messages = ConversationMemoryService(self.session).history(
            session_id, limit=200
        )
        return [
            {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "retrieved_context": message.retrieved_context,
                "citations": message.citations,
                "provider": message.provider,
                "model": message.model,
                "latency_ms": message.latency_ms,
                "token_usage": message.token_usage,
                "created_at": message.created_at,
            }
            for message in messages
        ]

    def _retrieval_result(self, result: VectorSearchResult) -> RetrievalResult:
        chunk = self.session.get(KnowledgeChunk, result.chunk_id)
        if chunk is None:
            msg = f"Knowledge chunk not found: {result.chunk_id}"
            raise ValueError(msg)
        return RetrievalResult(chunk=chunk, score=result.similarity_score)

    def _citation(self, result: RetrievalResult) -> Citation:
        return Citation(
            document=result.chunk.document_name,
            section=result.chunk.section,
            chunk=result.chunk.id,
            similarity_score=result.score,
        )

    def _context_text(self, chunks: list[ContextChunk]) -> str:
        return "\n\n".join(
            (
                f"[{index}] {chunk.document} / {chunk.section} "
                f"(chunk {chunk.chunk_id}, score {chunk.similarity_score})\n"
                f"{chunk.content}"
            )
            for index, chunk in enumerate(chunks, start=1)
        )

    def _citation_text(self, citations: list[Citation]) -> str:
        return "\n".join(
            (
                f"[{index}] document={citation.document}; "
                f"section={citation.section}; chunk={citation.chunk}; "
                f"score={citation.similarity_score}"
            )
            for index, citation in enumerate(citations, start=1)
        )

    def _extractive_answer(
        self,
        question: str,
        retrieved: list[RetrievalResult],
    ) -> str:
        if not retrieved:
            return "Insufficient supporting documentation."
        excerpts = " ".join(item.chunk.content for item in retrieved[:2])
        excerpt = excerpts[:700].strip()
        return (
            "Provider is not configured, so this response is an extractive "
            f"grounded summary for: {question}\n\n{excerpt}"
        )
