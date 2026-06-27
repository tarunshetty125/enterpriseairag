from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(frozen=True)
class VectorRecord:
    chunk_id: int
    document: str
    section: str
    content: str
    vector: list[float]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class VectorSearchResult:
    chunk_id: int
    document: str
    section: str
    content: str
    similarity_score: float
    metadata: dict[str, Any]


class VectorStore:
    """FAISS-backed vector index with a local NumPy fallback."""

    def __init__(self, index_dir: Path) -> None:
        self.index_dir = index_dir
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.records_path = self.index_dir / "knowledge_records.json"
        self.backend = "local_numpy"
        self._faiss: Any | None = None
        try:
            import faiss

            self._faiss = faiss
            self.backend = "faiss"
        except Exception:
            self._faiss = None

    def build(self, records: list[VectorRecord]) -> None:
        payload = [
            {
                "chunk_id": record.chunk_id,
                "document": record.document,
                "section": record.section,
                "content": record.content,
                "vector": record.vector,
                "metadata": record.metadata,
            }
            for record in records
        ]
        self.records_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        if self._faiss is not None and records:
            matrix = np.array([record.vector for record in records], dtype=np.float32)
            index = self._faiss.IndexFlatIP(matrix.shape[1])
            index.add(matrix)
            self._faiss.write_index(index, str(self.index_dir / "knowledge.faiss"))

    def search(self, query_vector: list[float], top_k: int) -> list[VectorSearchResult]:
        records = self._records()
        if not records:
            return []
        query = np.array(query_vector, dtype=np.float32)
        if self._faiss is not None and (self.index_dir / "knowledge.faiss").exists():
            index = self._faiss.read_index(str(self.index_dir / "knowledge.faiss"))
            scores, indexes = index.search(query.reshape(1, -1), top_k)
            return [
                self._result(records[int(index)], float(score))
                for score, index in zip(scores[0], indexes[0], strict=False)
                if int(index) >= 0
            ]
        scored = [
            (self._similarity(query, np.array(record.vector, dtype=np.float32)), record)
            for record in records
        ]
        scored.sort(key=lambda item: item[0], reverse=True)
        return [self._result(record, score) for score, record in scored[:top_k]]

    def stats(self) -> dict[str, int | str]:
        records = self._records()
        dimensions = len(records[0].vector) if records else 0
        return {
            "backend": self.backend,
            "index_size": len(records),
            "dimensions": dimensions,
        }

    def _records(self) -> list[VectorRecord]:
        if not self.records_path.exists():
            return []
        rows = json.loads(self.records_path.read_text(encoding="utf-8"))
        records: list[VectorRecord] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            records.append(
                VectorRecord(
                    chunk_id=int(row.get("chunk_id", 0)),
                    document=str(row.get("document", "")),
                    section=str(row.get("section", "")),
                    content=str(row.get("content", "")),
                    vector=[
                        float(value)
                        for value in row.get("vector", [])
                        if isinstance(value, int | float)
                    ],
                    metadata=dict(row.get("metadata", {})),
                )
            )
        return records

    def _similarity(self, left: np.ndarray, right: np.ndarray) -> float:
        if left.size == 0 or right.size == 0:
            return 0.0
        return round(float(np.dot(left, right)), 6)

    def _result(self, record: VectorRecord, score: float) -> VectorSearchResult:
        return VectorSearchResult(
            chunk_id=record.chunk_id,
            document=record.document,
            section=record.section,
            content=record.content,
            similarity_score=round(score, 6),
            metadata=record.metadata,
        )
