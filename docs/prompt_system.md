# Prompt System

Prompts are file-backed Markdown templates under:

`backend/app/prompts/templates`

Each prompt defines:

- name
- version
- description
- variables
- body

`PromptManager` owns loading and rendering. Prompt text is not duplicated across
services.

Implemented templates:

- `rag_chat`
- `policy_summary`
- `recommendation_explanation`
- `customer_context`
