from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib

from app.core.config import get_settings


class ModelArtifactStore:
    """Stores and loads versioned local model artifacts."""

    def __init__(self, artifact_root: Path | None = None) -> None:
        self.artifact_root = artifact_root or get_settings().ml.artifact_path
        self.artifact_root.mkdir(parents=True, exist_ok=True)

    def save(self, model_name: str, version: str, payload: dict[str, Any]) -> Path:
        model_dir = self.artifact_root / model_name
        model_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = model_dir / f"{model_name}_{version}.joblib"
        if artifact_path.exists():
            msg = f"Model artifact already exists: {artifact_path}"
            raise FileExistsError(msg)
        joblib.dump(payload, artifact_path)
        return artifact_path

    def load(self, artifact_path: str) -> dict[str, Any]:
        payload = joblib.load(Path(artifact_path))
        if not isinstance(payload, dict):
            msg = f"Invalid model artifact payload: {artifact_path}"
            raise ValueError(msg)
        return payload
