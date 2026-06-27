# Provider Architecture

All providers implement the same `AIProvider` interface:

- `chat()`
- `stream()`
- `health()`
- `list_models()`

Functional providers:

- Groq
- OpenAI

Future placeholders:

- Gemini
- Ollama
- Anthropic

Runtime provider settings are stored in SQLite. The frontend asks the backend
for providers and models dynamically; model names are not hardcoded in the UI.

If an API key is missing, the provider reports `not_configured` instead of
pretending to be online.
