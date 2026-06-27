# Context Builder

The Context Builder creates structured context objects for AI workflows. It assembles evidence from multiple services into a single payload that the prompt manager can render.

## Inputs

| Source | Data |
|--------|------|
| Customer profile | Name, demographics, income, credit score |
| Feature snapshot | Engineered features with version |
| Risk prediction | Risk level, confidence, feature importance |
| Segmentation | Segment label, cluster assignment |
| Behaviour profile | Flags, lifestyle indicators, spend patterns |
| Recommendations | Product scores, reasons, supporting features |
| RAG retrieval | Retrieved chunks with citations |

## Output

A structured dictionary with all evidence fields that maps directly to prompt template variables. The context is passed to the prompt manager for rendering and then to the AI Gateway.

## Design

The context builder is a pure data transformation — no API calls, no side effects. It ensures that the LLM receives consistent, complete evidence regardless of which upstream services produced it.
