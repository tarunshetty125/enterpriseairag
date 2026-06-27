# Interview Talking Points

## Architecture

This project is an AI platform rather than a single RAG chatbot. FastAPI exposes
versioned APIs over a modular backend with dataset services, feature store,
machine learning, NLP, recommendation rules, RAG orchestration, prompt
management, AI Gateway, and provider abstraction. The frontend is a
multi-page dashboard built with Next.js, TanStack Query, and shadcn/ui.

## Machine Learning

The ML layer trains and versions Random Forest risk prediction and KMeans
segmentation models. The registry stores metrics, feature lists, artifact paths,
dataset versions, feature versions, and active model state. Models are explicit
and versioned — not embedded in API calls.

## NLP

Transaction intelligence is deterministic. It normalizes transaction text,
extracts keywords/entities, classifies transaction categories, computes
sentiment, and produces behaviour profiles. This runs in sub-millisecond time
per transaction with zero external dependencies.

## RAG

Policy documents are loaded, chunked, embedded, indexed, retrieved, and cited.
The final report includes retrieved chunks and policy citations so answers are
grounded. The system uses FAISS for vector search with a NumPy fallback, and
sentence-transformers for embeddings with a deterministic hash fallback.

## AI Gateway

All LLM calls go through the AI Gateway, Provider Manager, and provider
interface. Groq and OpenAI can be switched at runtime without restarting the
backend. If credentials are missing, the system returns deterministic grounded
fallbacks instead of hallucinating.

## Explainability

Every final report exposes source evidence, confidence, feature importance,
recommendation reasons, retrieved chunks, citations, token usage, and workflow
trace. The LLM adds narrative value — it does not make decisions.

## Why This Design

**"Why not just call the LLM directly?"**
The AI Gateway centralizes retry, metrics, token accounting, and response normalization. Without it, every service would duplicate this logic.

**"Why train ML models when the LLM could do it?"**
ML predictions are reproducible, measurable, and explainable. The LLM summarizes structured evidence — it doesn't replace deterministic decisions.

**"Why SQLite?"**
This is a local demo. SQLite eliminates Docker, connection management, and credentials. SQLAlchemy abstracts the SQL layer, so PostgreSQL is a config change.

**"Why rules-based NLP?"**
Rules are fast, reproducible, and transparent. For a demo with ~2,500 transactions, they're sufficient and easy to explain.

## Limitations

The project is local and interview-focused. It is not a production banking
system. Authentication, authorization, audit-grade governance, cloud deployment,
PII controls, human approval workflows, and production monitoring are future
work. See `docs/known_limitations.md` for the full list.

## Future Improvements

- SHAP explanations for ML predictions
- spaCy-based entity extraction
- True token streaming for chat
- Analyst feedback loops
- Offline RAG evaluation sets
- Role-based access control
- Production observability and audit exports
