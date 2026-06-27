# RAG Pipeline

Phase 5 implements a local policy retrieval pipeline:

```text
Policy files
  -> Policy Loader
  -> Recursive Text Splitter
  -> Embedding Manager
  -> Vector Store
  -> Retriever
  -> Context Builder
  -> Prompt Manager
  -> AI Gateway
```

The vector store uses FAISS when installed and a NumPy cosine/dot-product
fallback otherwise. Embeddings use Sentence Transformers when installed and a
deterministic local hashing fallback otherwise.

Every chat response returns citations with document, section, chunk id,
similarity score, and evidence count through the API.

If no retrieved evidence meets the similarity threshold, the assistant returns:

`Insufficient supporting documentation.`
