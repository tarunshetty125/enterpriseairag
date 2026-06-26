# Synthetic Join Strategy

The public datasets used in Phase 2 do not share real customer IDs. To create a coherent local demo without inventing random joins, the platform uses deterministic synthetic linking.

## Customer ID Generation

Primary customer datasets generate IDs with:

```text
CUST-<sha256(dataset_namespace|source_record_id)[:12]>
```

The same source record always produces the same canonical customer ID.

## Cross-Dataset Linking

Datasets without a natural customer profile, such as loan and transaction datasets, are linked to existing customer anchors by hashing:

```text
sha256(dataset_namespace|source_record_id) % number_of_anchor_customers
```

This creates repeatable joins across runs while clearly documenting that the relationships are synthetic for demonstration purposes.

## Why This Approach

- Reproducible.
- Idempotent.
- No random seeds or non-deterministic joins.
- Honest about public dataset limitations.
- Good enough for an interview-ready local AI platform.
