# Project Metrics

Quantitative summary of the platform as of the current build.

## Codebase

| Metric | Count |
|--------|-------|
| Backend Python files | 129 |
| Backend lines of code | ~10,100 |
| Frontend TSX files | 54 |
| Frontend TS files | 10 |
| Integration test files | 5 |
| Documentation files | 20+ |
| API endpoints | 45 |
| SQLite tables | 20 |
| Backend modules | 16 |
| Frontend pages | 17 |

## Datasets

| Dataset | Source | Records | Purpose |
|---------|--------|---------|---------|
| Bank Customer Churn | Kaggle | ~10,000 | Customer demographics, credit scores |
| Credit Card Customers | Kaggle | ~10,000 | Products, credit limits, balances |
| Loan Prediction | Kaggle | ~600 | Loan applications, approval status |
| PaySim Transactions | Kaggle (sampled) | ~2,500 | Transaction descriptions, amounts |
| **Total canonical customers** | — | **~13,000** | — |
| **Total rows loaded** | — | **~16,100** | — |

## Machine Learning

| Model | Algorithm | Features | Metrics |
|-------|-----------|----------|---------|
| Risk Prediction | Random Forest Classifier | 8 engineered features | Accuracy, precision, recall, F1 |
| Customer Segmentation | KMeans Clustering | 8 engineered features | Silhouette score, inertia |

Both models are versioned in the model registry with artifact paths, training timestamps, dataset versions, and feature versions.

## NLP Pipeline

| Component | Method | Coverage |
|-----------|--------|----------|
| Text normalization | Regex + rules | All transactions |
| Keyword extraction | Frequency-based | All transactions |
| Entity extraction | Pattern matching | Merchants, amounts, categories |
| Category classification | Rules-based taxonomy | 10+ categories |
| Sentiment scoring | Keyword + rule signals | All transactions |
| Behaviour profiling | Aggregation + indicators | Per customer |

## RAG Knowledge Base

| Metric | Value |
|--------|-------|
| Policy documents | 5 (banking FAQ, credit card, home loan, insurance, investment) |
| Knowledge chunks | ~19 |
| Embedding model | sentence-transformers/all-MiniLM-L6-v2 (with local hash fallback) |
| Vector index | FAISS (with NumPy cosine fallback) |
| Similarity threshold | Configurable (default 0.18) |

## AI Provider

| Metric | Value |
|--------|-------|
| Active provider | Groq |
| Default model | llama-3.3-70b-versatile |
| Available models | 17 (dynamically loaded from Groq API) |
| Supported providers | Groq, OpenAI (3 placeholders for future) |
| Average chat latency | ~200–400ms |

## Technology Stack

| Category | Technologies |
|----------|-------------|
| Backend framework | FastAPI 0.115+ |
| ORM | SQLAlchemy 2.x |
| Database | SQLite |
| ML | scikit-learn, pandas, numpy, joblib |
| RAG | FAISS, sentence-transformers, LangChain text splitters |
| HTTP client | httpx |
| Frontend framework | Next.js 15 |
| UI components | shadcn/ui, Tailwind CSS |
| Charts | Recharts |
| State management | TanStack Query |

## Status

The platform is feature-complete for local demonstration. All services are operational, Groq integration is verified, and the frontend connects to all backend endpoints.
