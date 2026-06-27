# Synthetic Join Strategy

The public datasets do not share real customer IDs. The platform uses deterministic synthetic linking to create a coherent local demo.

## Customer ID Generation

A deterministic hash function generates `customer_id` values from source record attributes:

```
customer_id = "CUST-" + SHA256(source_dataset + ":" + source_record_id)[:12]
```

This ensures:
- The same source record always produces the same customer ID.
- Different datasets can link to the same customer when attribute matching succeeds.
- IDs are reproducible across ingestion runs.

## Cross-Dataset Linking

The linker matches customers across datasets using overlapping attributes (e.g., age, gender, geography). When a match is found, the existing `customer_id` is reused. When no match is found, a new customer is created.

This is intentionally approximate — the goal is a realistic-looking demo, not production entity resolution.

## Traceability

Every canonical record stores `source_dataset` and `source_record_id` so the original CSV row can be traced. The `external_references` JSON field stores additional source-specific metadata.
