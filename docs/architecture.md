# Architecture

## System Overview

The platform is a modular AI system where each layer builds on the previous:

```text
Data Foundation → Feature Store → ML → NLP → Recommendations → RAG → AI Gateway → Customer Intelligence
```

No layer calls downstream. The Customer Intelligence service is the only component that composes all prior layers.

## Component Diagram

```mermaid
graph LR
    subgraph "Data Layer"
        DS[Dataset Service]
        DB[(SQLite)]
        FS[Feature Store]
    end

    subgraph "ML Layer"
        TR[Training Pipeline]
        PR[Prediction Pipeline]
        MR[Model Registry]
        AS[Artifact Store]
    end

    subgraph "NLP Layer"
        TI[Transaction Intelligence]
        BE[Behaviour Engine]
    end

    subgraph "Intelligence Layer"
        RE[Recommendation Engine]
        RAG[RAG Service]
        CB[Context Builder]
    end

    subgraph "AI Layer"
        GW[AI Gateway]
        PM[Provider Manager]
        GP[Groq Provider]
        OP[OpenAI Provider]
    end

    subgraph "Composition"
        CI[Customer Intelligence Service]
    end

    DS --> DB
    FS --> DB
    TR --> MR
    TR --> AS
    PR --> AS
    TI --> DB
    BE --> TI
    RE --> DB
    RAG --> DB

    CI --> FS
    CI --> PR
    CI --> BE
    CI --> RE
    CI --> RAG
    CI --> GW
    GW --> PM
    PM --> GP
    PM --> OP
```

## Request Flow

A Customer Intelligence Report follows this sequence:

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as FastAPI
    participant CI as Intelligence Service
    participant FS as Feature Store
    participant ML as ML Pipeline
    participant NLP as NLP Pipeline
    participant REC as Recommendations
    participant RAG as RAG Service
    participant GW as AI Gateway
    participant LLM as Groq/OpenAI

    FE->>API: POST /customers/{id}/intelligence-report
    API->>CI: generate_report(customer_id)
    CI->>FS: get feature snapshot
    CI->>ML: predict risk + segment
    CI->>NLP: get behaviour profile
    CI->>REC: generate recommendations
    CI->>RAG: retrieve policy evidence
    CI->>CI: build structured context
    CI->>GW: chat(context + prompt)
    GW->>LLM: POST /chat/completions
    LLM-->>GW: response + usage
    GW-->>CI: normalized response
    CI->>CI: assemble report + persist
    CI-->>API: CustomerIntelligenceReport
    API-->>FE: JSON response
```

## Key Design Principles

- **Separation of concerns** — each module has a single responsibility.
- **Evidence-grounded AI** — the LLM summarizes structured evidence, never invents data.
- **Provider abstraction** — business logic never calls Groq or OpenAI directly.
- **Deterministic foundations** — ML, NLP, and recommendations are deterministic and reproducible.
- **Local-first** — everything runs on SQLite with no external services except the LLM API.

## Module Boundaries

| Module | Responsibility | Depends On |
|--------|---------------|------------|
| `datasets/` | Ingest, normalize, link public CSV data | `db/`, `core/` |
| `feature_store/` | Compute versioned customer features | `db/`, `datasets/` |
| `ml/` | Train models, predict, registry, explainability | `db/`, `feature_store/` |
| `nlp/` | Transaction classification, sentiment, behaviour | `db/` |
| `recommendation/` | Rules-based product scoring | `db/`, `nlp/` |
| `rag/` | Policy ingestion, embeddings, retrieval, chat | `db/`, `gateway/` |
| `gateway/` | AI request routing, metrics, retry | `providers/` |
| `providers/` | Groq/OpenAI adapters, health checks | External APIs |
| `intelligence/` | Customer Intelligence report composition | All above |
| `prompts/` | File-backed prompt templates | Filesystem |
