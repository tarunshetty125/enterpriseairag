from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.core.config import get_settings


@dataclass(frozen=True)
class PromptTemplate:
    name: str
    version: str
    description: str
    variables: list[str]
    body: str
    path: Path


class PromptRegistry:
    """Discovers prompt templates from the configured prompt directory."""

    def __init__(self, prompt_dir: Path | None = None) -> None:
        self.prompt_dir = prompt_dir or get_settings().ai.prompt_path

    def list_templates(self) -> list[PromptTemplate]:
        if not self.prompt_dir.exists():
            return []
        return [self._load(path) for path in sorted(self.prompt_dir.glob("*.md"))]

    def get(self, name: str) -> PromptTemplate:
        for template in self.list_templates():
            if template.name == name:
                return template
        msg = f"Prompt template not found: {name}"
        raise ValueError(msg)

    def _load(self, path: Path) -> PromptTemplate:
        text = path.read_text(encoding="utf-8")
        metadata: dict[str, str] = {}
        body = text
        if text.startswith("---"):
            _, meta_text, body = text.split("---", 2)
            for line in meta_text.strip().splitlines():
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()
        variables = [
            variable.strip()
            for variable in metadata.get("variables", "").split(",")
            if variable.strip()
        ]
        return PromptTemplate(
            name=metadata.get("name", path.stem),
            version=metadata.get("version", "v1"),
            description=metadata.get("description", ""),
            variables=variables,
            body=body.strip(),
            path=path,
        )


class PromptRenderer:
    """Renders registered prompt templates with explicit variables."""

    def render(self, template: PromptTemplate, variables: dict[str, object]) -> str:
        rendered = template.body
        missing = [
            variable for variable in template.variables if variable not in variables
        ]
        if missing:
            msg = f"Missing prompt variables: {', '.join(missing)}"
            raise ValueError(msg)
        for key, value in variables.items():
            rendered = rendered.replace("{{ " + key + " }}", str(value))
            rendered = rendered.replace("{{" + key + "}}", str(value))
        return rendered


class PromptManager:
    """Facade for prompt registry and rendering."""

    def __init__(self, prompt_dir: Path | None = None) -> None:
        self.registry = PromptRegistry(prompt_dir)
        self.renderer = PromptRenderer()

    def list_prompts(self) -> list[PromptTemplate]:
        return self.registry.list_templates()

    def get_prompt(self, name: str) -> PromptTemplate:
        return self.registry.get(name)

    def render(
        self, name: str, variables: dict[str, object]
    ) -> tuple[str, PromptTemplate]:
        template = self.registry.get(name)
        return self.renderer.render(template, variables), template
