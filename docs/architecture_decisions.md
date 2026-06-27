# Architecture Decisions

Key design choices and their rationale.

## Why FastAPI

FastAPI provides typed request/response schemas through Pydantic, automatic OpenAPI documentation, dependency injection for database sessions, and async support. For a local showcase that needs to demonstrate enterprise API design, FastAPI gives the most professional result with the least boilerplate.

**Alternative considered:** Flask. Rejected because it lacks native type validation and auto-generated API docs.

## Why Next.js

Next.js App Router provides file-based routing, server components, and a mature ecosystem. The frontend is a data-heavy dashboard with many pages — Next.js handles this naturally. TanStack Query manages server state, Tailwind CSS handles styling, and shadcn/ui provides accessible components.

**Alternative considered:** Vite + React Router. Would work but requires more manual routing setup and lacks the conventions that make the project structure self-documenting.

## Why SQLite

This is a local demo, not a deployed service. SQLite eliminates the need for database servers, Docker, or connection management. It stores everything in a single file that can be deleted and rebuilt. SQLAlchemy abstracts the SQL layer so switching to PostgreSQL would require only a connection string change.

**Trade-off:** No concurrent write support, no full-text search. Acceptable for a single-user demo.

## Why a Feature Store

The feature store creates a stable interface between raw data and ML models. Features are versioned and snapshotted per customer, so model training and prediction use the same feature definitions. This mirrors enterprise practice where feature engineering is a separate concern from model training.

**Alternative considered:** Computing features inline during prediction. Rejected because it couples feature logic to model code and makes versioning impossible.

## Why an AI Gateway

All LLM calls go through a single gateway (`AIGateway`) rather than calling providers directly. This centralizes:

- Retry logic for transient failures
- Token accounting and cost tracking
- Latency metrics recording
- Response normalization across providers
- Error handling with structured fallbacks

Without the gateway, every service that uses an LLM would need its own retry, metrics, and error handling code.

## Why Provider Abstraction

The `AIProvider` interface (`chat`, `stream`, `health`, `list_models`) lets the platform switch between Groq and OpenAI at runtime without restarting. Both use OpenAI-compatible APIs, so `OpenAICompatibleProvider` handles both through a shared base class. Adding a new provider means implementing four methods.

**Trade-off:** Slightly more indirection than calling Groq directly. Worth it because it demonstrates enterprise-grade extensibility.

## Why Groq and OpenAI

Groq provides fast inference for Llama models with an OpenAI-compatible API. OpenAI is the industry standard. Both share the same API contract, which validates the provider abstraction. The platform defaults to Groq because it offers free-tier access for demos.

## Why RAG Instead of Fine-tuning

RAG retrieves relevant policy documents at query time and includes them as context. This approach:

- Requires no model training or fine-tuning infrastructure
- Provides grounded citations that can be verified
- Updates instantly when policy documents change
- Works with any LLM provider

The RAG pipeline uses FAISS for vector search (with a NumPy fallback) and sentence-transformers for embeddings (with a deterministic hash fallback).

## Why ML Before LLM

The platform trains explicit ML models (risk prediction, segmentation) before using LLMs. The LLM summarizes structured ML output rather than making predictions directly. This ensures:

- Predictions are reproducible and explainable
- Model performance can be measured with standard metrics
- The LLM adds narrative value without replacing deterministic decisions
- The system works without an API key (deterministic fallback)

## Why Deterministic NLP

Transaction intelligence uses rules-based classification, keyword extraction, and sentiment scoring rather than LLM-based NLP. This keeps the NLP layer:

- Fast (sub-millisecond per transaction)
- Reproducible (same input always produces same output)
- Independent of API keys or external services
- Transparent (rules can be inspected and audited)

**Future improvement:** Add spaCy or a small local model for more sophisticated entity extraction.

## Key Trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| SQLite over PostgreSQL | Zero setup, single-file portability | No concurrency, no FTS |
| Rules-based NLP | Deterministic, fast, no dependencies | Less sophisticated than ML-based NLP |
| Static model list for Groq | Works offline, fast | May miss new models |
| FAISS with fallback | Works without FAISS installed | Fallback is slower for large indexes |
| Single-process backend | Simple deployment | No horizontal scaling |
| Cached intelligence reports | Fast repeated lookups | Cache invalidation on data change |
