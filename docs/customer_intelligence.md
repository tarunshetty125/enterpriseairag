# Customer Intelligence Platform

The Customer Intelligence Platform is the final composition layer for the local
enterprise AI financial showcase. It orchestrates prior services and exposes
their evidence in one relationship-manager workflow.

## Request Lifecycle

1. Load the canonical customer profile from SQLite.
2. Read the latest feature snapshot from the feature store.
3. Run the active risk prediction model.
4. Run the active segmentation model.
5. Generate deterministic transaction intelligence and behaviour profile.
6. Generate rules-based recommendations.
7. Retrieve policy evidence from the knowledge base.
8. Build a structured context payload.
9. Render the `customer_intelligence_report` prompt.
10. Send the request through the AI Gateway and active provider.
11. Persist the report, evidence, workflow trace, token usage, and cache metadata.

## Grounding Rules

The report treats ML, NLP, recommendation outputs, and retrieved policy chunks as
source-of-truth evidence. The LLM summarizes structured evidence only. If
provider credentials are not configured, the service returns a deterministic
grounded fallback narrative.

## Cache Strategy

Reports are cached by customer ID and input hash. The hash includes customer
metadata, feature version, model versions, behaviour timestamp, recommendations,
citations, provider, model, and report version.

## Exports

Reports can be exported as PDF, Markdown, or JSON. Each export preserves policy
citations and report metadata.
