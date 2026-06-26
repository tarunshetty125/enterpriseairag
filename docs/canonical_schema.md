# Canonical Schema

Phase 2 normalizes unrelated public datasets into one reusable financial schema.

## Tables

- `customers`: canonical customer profile fields, source references, and synthetic customer IDs.
- `loans`: loan records linked to customers.
- `transactions`: transaction records linked to customers.
- `products`: customer product holdings.
- `feature_snapshots`: versioned feature payloads for future ML and AI phases.
- `dataset_metadata`: dataset source, version, checksum, row count, import time, and status.
- `ingestion_runs`: each ingestion execution and result.

## Design Choices

The schema is intentionally broad enough for feature engineering but small enough for a local interview demo. Prediction tables are excluded from Phase 2 because no ML training or inference is implemented yet.
