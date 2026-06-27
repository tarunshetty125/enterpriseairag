from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LoadedPolicyDocument:
    name: str
    document_type: str
    source_path: Path
    version: str
    checksum: str
    text: str


class PolicyLoader:
    """Loads local policy documents from the configured policies directory."""

    def __init__(self, policy_dir: Path) -> None:
        self.policy_dir = policy_dir

    def load(self) -> list[LoadedPolicyDocument]:
        if not self.policy_dir.exists():
            return []
        documents: list[LoadedPolicyDocument] = []
        for path in sorted(self.policy_dir.iterdir()):
            if path.suffix.lower() not in {".md", ".txt", ".pdf"}:
                continue
            text = self._read(path)
            if not text.strip():
                continue
            checksum = hashlib.sha256(text.encode("utf-8")).hexdigest()
            documents.append(
                LoadedPolicyDocument(
                    name=path.name,
                    document_type=self._document_type(path.name),
                    source_path=path,
                    version=checksum[:12],
                    checksum=checksum,
                    text=text,
                )
            )
        return documents

    def _read(self, path: Path) -> str:
        if path.suffix.lower() == ".pdf":
            try:
                from pypdf import PdfReader

                reader = PdfReader(path)
                return "\n".join(page.extract_text() or "" for page in reader.pages)
            except Exception:
                return ""
        return path.read_text(encoding="utf-8")

    def _document_type(self, name: str) -> str:
        lowered = name.lower()
        if "loan" in lowered:
            return "loan_policy"
        if "insurance" in lowered:
            return "insurance_guide"
        if "investment" in lowered or "mutual" in lowered:
            return "investment_guide"
        if "credit" in lowered:
            return "credit_card_policy"
        return "banking_faq"
