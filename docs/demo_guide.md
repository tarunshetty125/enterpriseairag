# Demo Guide

Interview walkthrough for a 5–7 minute demonstration.

## Prerequisites

Start both servers before the demo:

```bash
# Terminal 1
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload

# Terminal 2
cd frontend && npm run dev
```

Ensure data is ingested and models are trained (one-time setup):

```bash
curl -X POST http://127.0.0.1:8000/api/v1/datasets/ingest
curl -X POST http://127.0.0.1:8000/api/v1/ml/train/risk
curl -X POST http://127.0.0.1:8000/api/v1/ml/train/segmentation
curl -X POST http://127.0.0.1:8000/api/v1/knowledge/ingest
```

## 1. Executive Dashboard (~1 min)

Open `http://localhost:3000`. Explain that this is an internal banking AI platform, not a standalone chatbot. Point out:
- Customer count, risk distribution, recommendation stats
- Knowledge base document count
- AI request count, active provider, and model
- Recent intelligence reports

## 2. Customer 360 (~1.5 min)

Click a customer from the dashboard. Walk through the tabs:
- **Overview** — demographics, credit score, income
- **Features** — engineered features from the feature store
- **Risk** — ML prediction with confidence and feature importance
- **Behaviour** — NLP-derived behaviour flags and lifestyle indicators
- **Transactions** — classified transactions with sentiment
- **Recommendations** — scored products with explanations
- **Policy Evidence** — RAG-retrieved chunks with citations
- **AI Report** — the generated intelligence report
- **Timeline** — workflow trace with per-stage timing

## 3. Generate Intelligence Report (~1.5 min)

Click "Generate Customer Report". Explain the orchestration:
- Feature store provides versioned features
- ML models predict risk and segment
- NLP produces behaviour profile
- Recommendation engine scores products
- RAG retrieves relevant policy evidence
- AI Gateway sends the composed context to Groq
- The report is assembled with full evidence chain

## 4. Explainability (~1 min)

Highlight evidence in the report:
- Risk drivers with feature importance
- Recommendation reasons with supporting features
- Citations linking to source policy documents
- Token usage and provider metadata
- Workflow trace showing per-stage timing

## 5. Exports (~30 sec)

Export the report as Markdown, JSON, or PDF. Mention that exports preserve citations for auditability.

## 6. Developer Console (~30 sec)

Open the Developer Console to show operational metrics:
- Provider and model settings
- Provider health status and latency
- Token usage, retrieved chunks
- Model versions, feature version, dataset version
- SQLite size, vector index size, report cache hits

## Talking Points During Demo

- "This is an AI platform, not a chatbot."
- "The LLM summarizes evidence — it doesn't make decisions."
- "I can switch providers at runtime without restarting."
- "Every recommendation has an explanation derived from rules, not generated text."
- "Citations trace back to policy documents for auditability."
