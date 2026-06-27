# Enterprise AI Financial Customer Intelligence Platform

Local, interview-ready AI platform foundation for a financial customer intelligence system. The project is intentionally scoped as a technical showcase, not a production banking application.

## Project Overview

This repository will evolve into an enterprise-style AI platform demonstrating machine learning, NLP, RAG, explainable AI, provider abstraction, and a modern React + FastAPI architecture.

Phase 1 establishes the foundation:

- Next.js 15 frontend shell with TypeScript, Tailwind CSS, shadcn/ui conventions, TanStack Query, Axios, and Lucide icons.
- FastAPI backend with versioned APIs, typed Pydantic Settings, SQLAlchemy 2.x, Alembic, SQLite initialization, and structured logging.
- Enterprise module boundaries for the approved AI platform architecture.
- Live Developer Console foundation backed by real health and settings endpoints.

## Architecture Summary

The approved architecture is frozen for future phases:

```text
FastAPI
  -> Workflow Engine
  -> Feature Store / ML / NLP / Recommendation / RAG
  -> Context Builder
  -> Prompt Builder
  -> AI Gateway
  -> Provider Manager
  -> Groq / OpenAI
```

Phase 1 does not implement ML, NLP, RAG, AI providers, workflow logic, or business logic. It creates the clean boundaries those systems will use.

Phase 2 adds the enterprise data foundation: public dataset ingestion, canonical schema, SQLite persistence, deterministic synthetic joins, data quality reporting, and a versioned feature store. It still does not implement ML predictions, AI providers, RAG, or LLM workflows.

Phase 3 adds the enterprise machine learning platform: explicit model training,
versioned artifacts, SQLite model registry, risk prediction, customer
segmentation, evaluation metrics, prediction logging, and explainability. It
still does not implement NLP, recommendations, AI providers, RAG, or chat.

Phase 4 adds deterministic NLP intelligence and rules-based recommendations:
transaction classification, entity extraction, sentiment signals, behaviour
profiles, explainable product recommendations, persistence, API endpoints, and
connected frontend pages. It still does not implement AI providers, RAG,
LangChain, FAISS, workflow orchestration, prompt builders, or chat.

Phase 5 adds the enterprise AI platform layer: AI Gateway, runtime provider
switching, prompt registry, structured context builder, local policy RAG,
knowledge ingestion, citations, chat memory, and connected AI UI pages. It still
does not implement customer intelligence reports, workflow orchestration, or
autonomous agents.

## Folder Structure

```text
enterprise-ai-financial-platform/
  frontend/       # Next.js 15 App Router application
  backend/        # FastAPI application
  data/           # Raw, processed, and policy data folders
  models/         # Versioned local ML artifacts
  vectorstore/    # Future FAISS artifacts
  docs/           # Project documentation
  scripts/        # Future development scripts
```

Backend module boundaries:

```text
backend/app/
  api/v1/
  core/
  db/
  gateway/
  providers/
  workflow/
  feature_store/
  ml/
  nlp/
  rag/
  recommendation/
  intelligence/
  analytics/
  developer_console/
  settings/
  utils/
```

Frontend route shell:

```text
frontend/app/
  dashboard/
  customers/
  analytics/
  model-registry/
  risk-prediction/
  segmentation/
  transaction-intelligence/
  behaviour/
  recommendations/
  knowledge/
  assistant/
  prompts/
  developer-console/
  settings/
```

## Technology Stack

Frontend:

- Next.js 15 App Router
- TypeScript
- Tailwind CSS
- shadcn/ui conventions
- TanStack Query
- Axios
- React Hook Form
- Zod
- Recharts
- Lucide Icons

Backend:

- FastAPI
- SQLAlchemy 2.x
- Alembic
- SQLite
- Pydantic Settings
- Structured JSON logging
- scikit-learn
- pandas
- numpy
- joblib

Phase 4 still uses deterministic Python services. spaCy/NLTK integrations are
reserved for deeper NLP expansion and are not required for the current local
demo path.

## Setup Instructions

Copy environment defaults:

```bash
cp .env.example .env
```

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Default URLs:

- Backend API: `http://127.0.0.1:8000/api/v1/health`
- Frontend: `http://localhost:3000`

## Development Workflow

Backend quality checks:

```bash
cd backend
ruff check .
black --check .
mypy app
alembic current
```

Frontend quality checks:

```bash
cd frontend
npm run typecheck
npm run lint
npm run build
```

## Phase 1 API Surface

Only these versioned endpoints exist in Phase 1:

- `GET /api/v1/health`
- `GET /api/v1/system-health`
- `GET /api/v1/settings/ai-processing`

## Phase 2 API Surface

- `GET /api/v1/datasets`
- `POST /api/v1/datasets/ingest`
- `GET /api/v1/datasets/status`
- `GET /api/v1/customers`
- `GET /api/v1/customers/{id}`
- `GET /api/v1/customers/{id}/features`
- `GET /api/v1/data-quality`
- `GET /api/v1/feature-store/status`

## Phase 3 API Surface

- `POST /api/v1/ml/train/risk`
- `POST /api/v1/ml/train/segmentation`
- `GET /api/v1/ml/models`
- `GET /api/v1/ml/models/{model}`
- `POST /api/v1/ml/models/{model_id}/activate`
- `POST /api/v1/ml/predict/risk`
- `POST /api/v1/ml/predict/segment`
- `GET /api/v1/ml/evaluation`
- `GET /api/v1/ml/feature-importance`

## Phase 4 API Surface

- `GET /api/v1/transactions/{customer_id}/insights`
- `GET /api/v1/customers/{customer_id}/behaviour`
- `POST /api/v1/recommendations/generate/{customer_id}`
- `GET /api/v1/recommendations/{customer_id}`
- `GET /api/v1/recommendation-rules`
- `GET /api/v1/intelligence/status`

## Phase 5 API Surface

- `GET /api/v1/providers`
- `GET /api/v1/providers/models`
- `POST /api/v1/providers/switch`
- `GET /api/v1/providers/status`
- `PATCH /api/v1/providers/settings`
- `POST /api/v1/knowledge/ingest`
- `GET /api/v1/knowledge/documents`
- `GET /api/v1/knowledge/status`
- `POST /api/v1/chat`
- `GET /api/v1/chat/sessions`
- `GET /api/v1/chat/{session_id}`
- `GET /api/v1/prompts`
- `GET /api/v1/prompts/{name}`

## Roadmap

1. Phase 1: Enterprise foundation, configuration, SQLite, shell UI.
2. Phase 2: Dataset ingestion, feature engineering, feature store.
3. Phase 3: ML models, model registry, explainability.
4. Phase 4: NLP intelligence, behaviour profiles, recommendation engine.
5. Phase 5: RAG, embeddings, FAISS-compatible index, AI gateway, Groq/OpenAI switching.
6. Phase 6: Full dashboard, Customer 360, analytics, developer console, settings.
7. Phase 7: Tests, performance, documentation, demo preparation.
