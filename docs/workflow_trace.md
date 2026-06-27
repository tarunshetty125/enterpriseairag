# Workflow Trace

Workflow tracing records the execution timeline of a Customer Intelligence report. It captures each stage's source, status, and duration.

## Implementation

The trace is implemented as a lightweight list inside `CustomerIntelligenceService`. Each stage appends a trace entry before and after execution. No external tracing framework is needed.

## Trace Entry Format

```json
{
  "stage": "Risk Model",
  "source": "ml_prediction",
  "status": "success",
  "durationMs": 18.87,
  "details": "RiskPredictionResult"
}
```

## Stages

| Stage | Source | Description |
|-------|--------|-------------|
| Customer Profile | `customers` | Load canonical profile |
| Feature Store | `feature_snapshots` | Load feature snapshot |
| Risk Model | `ml_prediction` | Run risk prediction |
| Segmentation | `ml_prediction` | Run segmentation |
| Behaviour Engine | `behaviour_profiles` | Load/generate behaviour profile |
| Transaction Intelligence | `transaction_insights` | Load NLP insights |
| Recommendation Engine | `recommendations` | Generate recommendations |
| RAG | `knowledge_chunks` | Retrieve policy evidence |
| Provider | `ai_gateway` | LLM call through gateway |
| Customer Intelligence Report | `customer_intelligence_reports` | Final assembly |

## Access

The workflow trace is accessible via `GET /api/v1/customers/{id}/workflow-trace` and is also included in the full intelligence report response.
