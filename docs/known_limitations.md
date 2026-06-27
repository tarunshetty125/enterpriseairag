# Known Limitations

This project is a local technical showcase, not a production banking system. The following limitations are intentional scope constraints.

## Security

- No authentication or authorization. All endpoints are public.
- No role-based access control.
- API keys are stored in `.env` and loaded as environment variables.
- No PII masking or data encryption at rest.

## Data

- Datasets are public Kaggle data, not real banking data.
- Customer IDs are synthetically generated via deterministic hashing.
- Cross-dataset joins are synthetic (customers don't have real relationships across datasets).
- Transaction descriptions are simulated and may not reflect real banking patterns.

## Scalability

- SQLite does not support concurrent writes. The backend is single-process.
- FAISS index is stored on disk and loaded into memory. Not suitable for large document collections.
- No caching layer (Redis, etc.) beyond SQLite-based report caching.
- No background task queue (Celery, etc.). All processing is synchronous.

## Machine Learning

- Models are Random Forest and KMeans — effective for the demo but not state-of-the-art.
- No hyperparameter tuning, cross-validation, or automated retraining.
- No SHAP or LIME explanations — feature importance is model-native.
- No A/B testing or model comparison framework.
- No drift detection or monitoring.

## NLP

- Transaction classification is rules-based, not ML-based.
- Entity extraction uses pattern matching, not NER models.
- Sentiment scoring is keyword-based, not trained on financial text.
- No spaCy, NLTK, or transformer-based NLP.

## RAG

- Knowledge base is 5 demo policy documents (~19 chunks).
- No document versioning or incremental re-indexing.
- Embeddings fall back to deterministic hashing when sentence-transformers is unavailable.
- No hybrid search (keyword + semantic).
- No re-ranking or answer quality evaluation.

## AI Provider

- Streaming is implemented as a single-chunk passthrough (not true token streaming).
- No cost budgets or rate limiting.
- No prompt caching or response caching at the provider level.
- Anthropic, Gemini, and Ollama are placeholder stubs.

## Frontend

- No offline support or PWA capabilities.
- No dark/light mode toggle (dark mode only).
- No internationalization.
- No accessibility audit.

## Future Improvements

- Add real bank-approved policy PDFs for RAG.
- Add SHAP explanations for ML predictions.
- Add analyst feedback loops for recommendations.
- Add offline evaluation sets for RAG answer quality.
- Add role-based access control.
- Add production observability (structured metrics, tracing).
- Add spaCy-based entity extraction.
- Add true streaming for chat responses.
- Add PostgreSQL support for multi-user deployments.
- Add automated model retraining on data refresh.
