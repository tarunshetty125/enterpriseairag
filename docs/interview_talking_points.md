# Interview Talking Points

## Architecture

This project is an AI platform rather than a single RAG chatbot. FastAPI exposes
versioned APIs over a modular backend with dataset services, feature store,
machine learning, NLP, recommendation rules, RAG orchestration, prompt
management, AI Gateway, and provider abstraction.

## Machine Learning

The ML layer trains and versions Random Forest risk prediction and KMeans
segmentation models. The registry stores metrics, feature lists, artifact paths,
dataset versions, feature versions, and active model state.

## NLP

Transaction intelligence is deterministic. It normalizes transaction text,
extracts keywords/entities, classifies transaction categories, computes
sentiment, and produces behaviour profiles.

## RAG

Policy documents are loaded, chunked, embedded, indexed, retrieved, and cited.
The final report includes retrieved chunks and policy citations so answers are
grounded.

## AI Gateway

All LLM calls go through the AI Gateway, Provider Manager, and provider
interface. Groq and OpenAI can be switched at runtime without restarting the
backend. If credentials are missing, the system returns deterministic grounded
fallbacks instead of hallucinating.

## Explainability

Every final report exposes source evidence, confidence, feature importance,
recommendation reasons, retrieved chunks, citations, token usage, and workflow
trace.

## Limitations

The project is local and interview-focused. It is not a production banking
system. Authentication, authorization, audit-grade governance, cloud deployment,
PII controls, human approval workflows, and production monitoring are future
work.

## Future Improvements

- Add real bank-approved policy PDFs.
- Add SHAP explanations.
- Add analyst feedback loops.
- Add offline evaluation sets for RAG answers.
- Add role-based access control.
- Add production observability and audit exports.
