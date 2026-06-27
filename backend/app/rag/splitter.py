from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    chunk_index: int
    section: str
    content: str
    token_count: int


class RecursiveTextSplitter:
    """LangChain recursive splitter with a deterministic local fallback."""

    def __init__(self, chunk_size: int, overlap: int = 80) -> None:
        self.chunk_size = max(200, chunk_size)
        self.overlap = min(overlap, self.chunk_size // 4)

    def split(self, text: str) -> list[TextChunk]:
        sections = self._sections(text)
        chunks: list[TextChunk] = []
        for section, content in sections:
            for chunk_text in self._split_section(content):
                chunks.append(
                    TextChunk(
                        chunk_index=len(chunks),
                        section=section,
                        content=chunk_text,
                        token_count=len(chunk_text.split()),
                    )
                )
        return chunks

    def _split_section(self, content: str) -> list[str]:
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.overlap,
                separators=["\n\n", "\n", ". ", " ", ""],
            )
            return [
                chunk.strip() for chunk in splitter.split_text(content) if chunk.strip()
            ]
        except Exception:
            return self._split_section_locally(content)

    def _split_section_locally(self, content: str) -> list[str]:
        words = content.split()
        chunks: list[str] = []
        start = 0
        while start < len(words):
            end = min(len(words), start + self.chunk_size)
            chunks.append(" ".join(words[start:end]))
            if end == len(words):
                break
            start = max(0, end - self.overlap)
        return chunks

    def _sections(self, text: str) -> list[tuple[str, str]]:
        current = "General"
        rows: list[tuple[str, list[str]]] = [(current, [])]
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                current = stripped.lstrip("#").strip() or "General"
                rows.append((current, []))
                continue
            rows[-1][1].append(stripped)
        return [
            (section, " ".join(line for line in lines if line))
            for section, lines in rows
            if " ".join(line for line in lines if line).strip()
        ]
