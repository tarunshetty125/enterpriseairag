# 📚 Enterprise AI Financial Customer Intelligence Platform — Project Overview

Local, interview-ready AI platform that composes machine learning, NLP, RAG, explainable AI, and provider-abstracted LLM integration into a unified financial customer intelligence system.

## How It Works

Given a **Customer ID**, the platform orchestrates 7 services to generate a **Customer Intelligence Report**:

1. **Canonical Data** — normalized from four public financial datasets into one schema
2. **Feature Store** — deterministic, versioned customer features
3. **ML Predictions** — Random Forest risk scoring and KMeans segmentation
4. **NLP Intelligence** — transaction classification, entity extraction, sentiment, and behaviour profiling
5. **Recommendation Engine** — rules-based product suitability scoring with explainable reasons
6. **RAG Retrieval** — policy document search with FAISS indexing and grounded citations
7. **AI Gateway** — provider-abstracted LLM call through Groq or OpenAI with retry, metrics, and token accounting

---

## 🏗️ System Architecture

```mermaid
graph TD
    User["👤 User"] --> FE["Next.js 15 Frontend"]
    FE -->|REST API| API["FastAPI /api/v1"]

    API --> DS["📊 Dataset Service"]
    API --> FS["🧮 Feature Store"]
    API --> ML["🤖 ML Platform"]
    API --> NLP["📝 NLP Pipeline"]
    API --> REC["💡 Recommendation Engine"]
    API --> RAG["🔍 RAG Service"]
    API --> CI["📋 Customer Intelligence"]
    API --> GW["🌐 AI Gateway"]

    CI --> FS
    CI --> ML
    CI --> NLP
    CI --> REC
    CI --> RAG
    CI --> GW

    GW --> PM["Provider Manager"]
    PM --> GROQ["Groq API"]
    PM --> OAI["OpenAI API"]

    RAG --> EMB["Embedding Manager"]
    RAG --> VS["FAISS Vector Store"]
    RAG --> CB["Context Builder"]

    ML --> MR["Model Registry"]
    ML --> AS["Artifact Store"]

    subgraph Database
        DB[("SQLite — enterprise_ai_financial_platform.db")]
    end

    DS --> DB
    FS --> DB
    ML --> DB
    NLP --> DB
    REC --> DB
    RAG --> DB
    CI --> DB
    GW --> DB
```

---

## 🔄 Data Flow Pipeline

```mermaid
flowchart LR
    subgraph Ingestion
        CSV1["bank_customer_churn.csv"]
        CSV2["credit_card_customers.csv"]
        CSV3["loan_prediction.csv"]
        CSV4["paysim_transactions_sample.csv"]
    end

    subgraph Processing
        NORM["Normalize & Link"]
        FE["Feature Engineering"]
    end

    subgraph ML Models
        RF["Random Forest — Risk"]
        KM["KMeans — Segmentation"]
    end

    subgraph Intelligence
        NLP["NLP Analysis"]
        REC["Recommendations"]
        RAG["RAG Retrieval"]
        LLM["LLM Summary"]
    end

    CSV1 & CSV2 & CSV3 & CSV4 --> NORM --> FE
    FE --> RF & KM
    RF & KM --> REPORT["📋 Customer Intelligence Report"]
    NLP & REC & RAG & LLM --> REPORT
    FE --> NLP
    FE --> REC
```

---

## 🧩 Component Breakdown

### 📊 Dataset Service — Data Ingestion & Normalization

```mermaid
flowchart TD
    subgraph Raw Datasets
        A["bank_customer_churn.csv — 669 KB"]
        B["credit_card_customers.csv — 438 KB"]
        C["loan_prediction.csv — 37 KB"]
        D["paysim_transactions_sample.csv — 181 KB"]
    end

    A & B & C & D --> INGEST["Ingestion Service"]
    INGEST --> NORM["Schema Normalization"]
    NORM --> LINK["Cross-Dataset Linking"]
    LINK --> DB[("SQLite — Unified Customer Table")]
```

---

### 🧮 Feature Store — Feature Engineering

```mermaid
flowchart LR
    RAW["Raw Customer Data"] --> FE["Feature Engine"]
    FE --> F1["Balance Metrics"]
    FE --> F2["Transaction Frequency"]
    FE --> F3["Credit Utilization"]
    FE --> F4["Account Age"]
    FE --> F5["Activity Scores"]
    F1 & F2 & F3 & F4 & F5 --> STORE["Versioned Feature Store"]
```

---

### 🤖 ML Platform — Training & Prediction

```mermaid
flowchart TD
    FEATURES["Feature Store"] --> TRAIN["Training Pipeline"]
    TRAIN --> RF["Random Forest Classifier"]
    TRAIN --> KM["KMeans Clustering"]
    RF --> REGISTRY["Model Registry"]
    KM --> REGISTRY
    REGISTRY --> ARTIFACTS["Joblib Artifacts"]
    
    FEATURES --> PREDICT["Prediction Service"]
    REGISTRY --> PREDICT
    PREDICT --> RISK["Risk Score 0–1"]
    PREDICT --> SEG["Customer Segment"]
    PREDICT --> EXPLAIN["Feature Importance"]
```

---

### 📝 NLP Pipeline — Transaction Intelligence

```mermaid
flowchart TD
    TX["Customer Transactions"] --> CLASS["Transaction Classifier"]
    TX --> ENT["Entity Extractor"]
    TX --> SENT["Sentiment Analyzer"]
    TX --> BEH["Behaviour Profiler"]

    CLASS --> CAT["Categories: Salary, Rent, Groceries..."]
    ENT --> ENTITIES["Merchants, Amounts, Dates"]
    SENT --> SENTIMENT["Positive / Negative / Neutral"]
    BEH --> PROFILE["Spending Habits & Patterns"]
```

---

### 💡 Recommendation Engine

```mermaid
flowchart LR
    PROFILE["Customer Profile"] --> RULES["Rules Engine"]
    RULES --> SCORE["Product Suitability Scoring"]
    SCORE --> R1["Premium Credit Card ✅"]
    SCORE --> R2["Home Loan ⚠️"]
    SCORE --> R3["Investment Plan ✅"]
    R1 & R2 & R3 --> REASONS["Explainable Reasons"]
```

---

### 🔍 RAG Service — Retrieval Augmented Generation

```mermaid
flowchart TD
    DOCS["Policy Documents — Markdown"] --> SPLIT["Text Splitter — LangChain"]
    SPLIT --> EMB["sentence-transformers Embeddings"]
    EMB --> FAISS["FAISS Vector Index"]

    QUERY["User Question"] --> QEMB["Query Embedding"]
    QEMB --> SEARCH["Similarity Search"]
    FAISS --> SEARCH
    SEARCH --> CONTEXT["Retrieved Chunks + Citations"]
    CONTEXT --> LLM["LLM — Groq / OpenAI"]
    LLM --> ANSWER["Grounded Answer with Citations"]
```

---

### 🌐 AI Gateway — Provider Abstraction

```mermaid
flowchart TD
    REQ["LLM Request"] --> GW["AI Gateway"]
    GW --> ROUTE["Provider Router"]
    ROUTE --> GROQ["Groq API"]
    ROUTE --> OAI["OpenAI API"]
    
    GW --> RETRY["Retry Logic"]
    GW --> TOKENS["Token Counter"]
    GW --> METRICS["Usage Metrics"]
    GW --> COST["Cost Tracking"]

    GROQ & OAI --> RESP["LLM Response"]
    RESP --> GW
```

---

## 🛠️ Technology Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | Next.js 15, TypeScript, Tailwind CSS, shadcn/ui, TanStack Query, Recharts |
| **Backend** | FastAPI, SQLAlchemy 2.x, Alembic, Pydantic Settings |
| **ML** | scikit-learn, pandas, numpy, joblib |
| **NLP** | Deterministic Python (rules-based classification, extraction, sentiment) |
| **RAG** | FAISS, sentence-transformers, LangChain text splitters |
| **AI Providers** | Groq, OpenAI (via OpenAI-compatible HTTP adapter) |
| **Database** | SQLite (20 tables) |
| **HTTP Client** | httpx |

---

## 📂 Project Structure

```
enterprise-ai-financial-platform/
  backend/                 # FastAPI application
    app/
      api/v1/              # 45 versioned REST endpoints
      core/                # Configuration, logging
      db/                  # SQLAlchemy engine, session, base
      datasets/            # Dataset ingestion, normalization, linking
      feature_store/       # Deterministic feature engineering
      gateway/             # AI Gateway, metrics, retry, routing
      intelligence/        # Customer Intelligence reports
      ml/                  # Training, prediction, registry, explainability
      models/              # SQLAlchemy ORM models (20 tables)
      nlp/                 # Transaction classification, entities, sentiment
      prompts/             # File-backed prompt templates
      providers/           # Groq, OpenAI, provider abstraction
      rag/                 # Embeddings, vector store, retrieval, chat
      recommendation/      # Rules-based product recommendations
      schemas/             # Pydantic request/response schemas
    tests/                 # Integration tests
  frontend/                # Next.js 15 application
    app/                   # 17 pages (App Router)
    components/            # Reusable UI components
    hooks/                 # Custom React hooks
    lib/                   # API client, utilities
    types/                 # TypeScript type definitions
  data/                    # Raw datasets, processed data, policy documents
  models/                  # Versioned ML artifacts (joblib)
  vectorstore/             # FAISS index and knowledge records
  docs/                    # Architecture and design documentation
  scripts/                 # Development and verification scripts
```

---

## 🚀 Quick Start

```bash
# Cross-platform setup
python scripts/setup_environment.py
python scripts/run_backend.py     # Terminal 1
python scripts/run_frontend.py    # Terminal 2

# Ingest data & train models
curl -X POST http://127.0.0.1:8000/api/v1/datasets/ingest
curl -X POST http://127.0.0.1:8000/api/v1/ml/train/risk
curl -X POST http://127.0.0.1:8000/api/v1/ml/train/segmentation
curl -X POST http://127.0.0.1:8000/api/v1/knowledge/ingest
```

Open `http://localhost:3000` to access the platform.

---

## 🎯 Key Interview Topics Covered

- ✅ Full-stack development (Next.js + FastAPI)
- ✅ Machine Learning (Random Forest, KMeans, scikit-learn)
- ✅ NLP (text classification, entity extraction, sentiment analysis)
- ✅ RAG (Retrieval Augmented Generation with FAISS)
- ✅ LLM integration (Groq/OpenAI with provider abstraction)
- ✅ Data engineering (ETL, normalization, feature engineering)
- ✅ API design (45 RESTful endpoints, versioned)
- ✅ Database design (20 SQLite tables, SQLAlchemy ORM)
- ✅ Explainable AI (feature importance, confidence scores, citations)
- ✅ Software architecture (service pattern, provider abstraction, gateway)
