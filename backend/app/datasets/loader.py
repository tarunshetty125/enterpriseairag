from __future__ import annotations

import csv
import hashlib
import urllib.request
from pathlib import Path

from app.core.config import get_settings
from app.datasets.catalog import DatasetDefinition
from app.datasets.types import RawRow


class DatasetLoader:
    """Loads public CSV datasets into immutable local raw files."""

    def __init__(self) -> None:
        settings = get_settings()
        self.raw_path = settings.data.raw_path
        self.raw_path.mkdir(parents=True, exist_ok=True)

    def ensure_local_csv(self, definition: DatasetDefinition) -> Path:
        target_path = self.raw_path / definition.filename
        if target_path.exists():
            return target_path

        if definition.sample_rows is None:
            urllib.request.urlretrieve(definition.source, target_path)
            return target_path

        with urllib.request.urlopen(definition.source, timeout=60) as response:
            text_stream = (line.decode("utf-8") for line in response)
            with target_path.open("w", encoding="utf-8", newline="") as target:
                for index, line in enumerate(text_stream):
                    if index > definition.sample_rows:
                        break
                    target.write(line)

        return target_path

    def load_csv(
        self, definition: DatasetDefinition
    ) -> tuple[list[RawRow], list[str], str]:
        path = self.ensure_local_csv(definition)
        content = path.read_bytes()
        checksum = hashlib.sha256(content).hexdigest()

        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = [{key: value for key, value in row.items()} for row in reader]
            columns = list(reader.fieldnames or [])

        return rows, columns, checksum
