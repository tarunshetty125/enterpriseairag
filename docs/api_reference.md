# API Reference

All endpoints are prefixed with `/api/v1`. The backend runs at `http://127.0.0.1:8000`.

## Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Application health check |
| GET | `/system-health` | Backend, database, and provider status |

## Datasets

| Method | Path | Description |
|--------|------|-------------|
| GET | `/datasets` | List ingested dataset metadata |
| POST | `/datasets/ingest` | Ingest all raw CSV datasets |
| GET | `/datasets/status` | Dataset ingestion status summary |

## Customers

| Method | Path | Description |
|--------|------|-------------|
| GET | `/customers` | Paginated customer list |
| GET | `/customers/{id}` | Customer detail with products and loans |
| GET | `/customers/{id}/features` | Feature store snapshot for customer |

## Data Quality

| Method | Path | Description |
|--------|------|-------------|
| GET | `/data-quality` | Data quality report across datasets |

## Feature Store

| Method | Path | Description |
|--------|------|-------------|
| GET | `/feature-store/status` | Feature version and snapshot statistics |

## Machine Learning

| Method | Path | Description |
|--------|------|-------------|
| POST | `/ml/train/risk` | Train risk prediction model |
| POST | `/ml/train/segmentation` | Train customer segmentation model |
| GET | `/ml/models` | List all registered models |
| GET | `/ml/models/{model}` | Model detail with metrics |
| POST | `/ml/models/{id}/activate` | Set model as active |
| POST | `/ml/predict/risk` | Predict risk for a customer |
| POST | `/ml/predict/segment` | Predict segment for a customer |
| GET | `/ml/evaluation` | Evaluation metrics for active models |
| GET | `/ml/feature-importance` | Feature importance for active models |

## Intelligence

| Method | Path | Description |
|--------|------|-------------|
| GET | `/transactions/{id}/insights` | NLP-processed transaction insights |
| GET | `/customers/{id}/behaviour` | Behaviour profile |
| POST | `/recommendations/generate/{id}` | Generate recommendations for customer |
| GET | `/recommendations/{id}` | Get existing recommendations |
| GET | `/recommendation-rules` | List recommendation rules |
| GET | `/intelligence/status` | Intelligence pipeline status |

## Knowledge Base (RAG)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/knowledge/ingest` | Ingest and index policy documents |
| GET | `/knowledge/documents` | List indexed documents |
| GET | `/knowledge/status` | Knowledge base and vector store status |

## Chat

| Method | Path | Description |
|--------|------|-------------|
| POST | `/chat` | Send a chat message (RAG-grounded) |
| GET | `/chat/sessions` | List chat sessions |
| GET | `/chat/{session_id}` | Get session messages |

## Providers

| Method | Path | Description |
|--------|------|-------------|
| GET | `/providers` | List all providers with health status |
| GET | `/providers/models` | Models for active provider |
| POST | `/providers/switch` | Switch provider and model at runtime |
| GET | `/providers/status` | Provider settings, health, and metrics |
| PATCH | `/providers/settings` | Update AI processing parameters |

## Customer Intelligence

| Method | Path | Description |
|--------|------|-------------|
| POST | `/customers/{id}/intelligence-report` | Generate intelligence report |
| GET | `/customers/{id}/intelligence-report` | Get latest cached report |
| GET | `/customers/{id}/workflow-trace` | Workflow execution trace |
| GET | `/customers/{id}/intelligence-report/export` | Export as PDF/Markdown/JSON |
| GET | `/intelligence/reports/recent` | Recent reports across customers |
| GET | `/intelligence/showcase-metrics` | Aggregated showcase metrics |

## Prompts

| Method | Path | Description |
|--------|------|-------------|
| GET | `/prompts` | List registered prompt templates |
| GET | `/prompts/{name}` | Get prompt template detail |

## Settings

| Method | Path | Description |
|--------|------|-------------|
| GET | `/settings/ai-processing` | Current AI processing configuration |
