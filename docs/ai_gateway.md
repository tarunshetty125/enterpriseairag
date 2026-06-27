# AI Gateway

Phase 5 introduces the AI Gateway as the only path to LLM providers.

## Components

- `AIGateway`: public entry point for LLM requests.
- `RequestRouter`: selects the active runtime provider.
- `ResponseNormalizer`: converts provider responses into one internal shape.
- `MetricsCollector`: stores latency, token usage, context size, and chunk counts.
- `RetryPolicy`: retries transient provider calls.
- `StreamingAdapter`: keeps streaming behind the same provider interface.
- `TokenAccounting`: estimates tokens when providers do not return usage.

No business service calls Groq or OpenAI directly.

## Scope

The gateway explains or summarizes retrieved and structured data. It does not
make lending, investment, insurance, or product decisions.
