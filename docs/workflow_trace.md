# Workflow Trace

Workflow tracing is implemented as a lightweight execution timeline inside
`CustomerIntelligenceService`. It intentionally avoids a new workflow framework
so the project stays aligned with the approved architecture.

## Tracked Stages

- Customer Profile
- Feature Store
- Risk Model
- Segmentation
- Behaviour Engine
- Transaction Intelligence
- Recommendation Engine
- RAG
- Provider
- Customer Intelligence Report
- Report Cache

Each stage records stage name, source system, status, duration in milliseconds,
and human-readable details.

## Why It Matters

The trace turns the demo from a black-box chatbot into an observable AI
platform. Interviewers can see where data, ML, retrieval, prompts, and provider
execution contribute to the final report.
