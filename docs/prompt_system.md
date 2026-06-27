# Prompt System

Prompts are file-backed Markdown templates stored in `backend/app/prompts/templates/`.

## Templates

| Template | Purpose |
|----------|---------|
| `chat_with_context.md` | RAG-grounded chat responses |
| `customer_intelligence_report.md` | Full intelligence report narrative |

## Variables

Templates use Python `str.format()` placeholders. The Context Builder produces the variable values, and the Prompt Manager renders the final prompt.

## Versioning

Each template has a version identifier. When the Customer Intelligence report is cached, the prompt version is part of the cache key. Changing the template invalidates the cache.

## Prompt Manager

The `PromptManager` (`prompts/manager.py`) loads templates from disk, validates variable completeness, and renders final prompts. Templates are listed via `GET /api/v1/prompts` and inspected via `GET /api/v1/prompts/{name}`.
