from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class EmbeddingResult:
    vector: list[float]
    metadata: dict[str, Any]


class EmbeddingManager:
    """Embeds text with Sentence Transformers when available, else local hashing."""

    def __init__(self, model_name: str, dimensions: int = 128) -> None:
        self.model_name = model_name
        self.dimensions = dimensions
        self.backend = "local_hashing"
        self._model: Any | None = None
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(model_name)
            self.backend = "sentence_transformers"
        except Exception:
            self._model = None

    def embed(self, text: str) -> EmbeddingResult:
        if self._model is not None:
            vector = self._model.encode([text], normalize_embeddings=True)[0]
            values = [float(item) for item in vector]
            return EmbeddingResult(
                vector=values,
                metadata={
                    "embedding_model": self.model_name,
                    "embedding_backend": self.backend,
                    "dimensions": len(values),
                },
            )
        values = self._hash_embedding(text)
        return EmbeddingResult(
            vector=values,
            metadata={
                "embedding_model": self.model_name,
                "embedding_backend": self.backend,
                "dimensions": self.dimensions,
            },
        )

    def embed_many(self, texts: list[str]) -> list[EmbeddingResult]:
        return [self.embed(text) for text in texts]

    def _hash_embedding(self, text: str) -> list[float]:
        vector = np.zeros(self.dimensions, dtype=np.float32)
        tokens = [token.lower() for token in text.split() if token.strip()]
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(float(np.dot(vector, vector)))
        if norm > 0:
            vector = vector / norm
        return [round(float(item), 8) for item in vector]
