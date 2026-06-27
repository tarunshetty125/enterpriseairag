# Canonical Schema

The canonical schema normalizes four unrelated public datasets into one coherent customer model.

## Tables

| Table | Primary Key | Description |
|-------|-------------|-------------|
| `customers` | `customer_id` (String) | Unified customer profiles |
| `loans` | `id` (Integer) | Loan records linked to customers |
| `transactions` | `id` (Integer) | Transaction records linked to customers |
| `products` | `id` (Integer) | Financial products held by customers |

All tables include `source_dataset` and `source_record_id` columns for traceability back to the original CSV row.

## Customer Fields

| Field | Type | Source |
|-------|------|--------|
| `customer_id` | String(32) | Deterministic hash (see synthetic join strategy) |
| `full_name` | String | Churn dataset or generated |
| `age` | Integer | Churn dataset |
| `gender` | String | Churn / credit card dataset |
| `geography` | String | Churn dataset |
| `education` | String | Credit card dataset |
| `income_category` | String | Credit card dataset |
| `estimated_income` | Float | Churn dataset |
| `credit_score` | Integer | Churn dataset |
| `savings_balance` | Float | Derived from products |
| `tenure_months` | Integer | Churn dataset |

## Relationships

Each customer has zero-to-many loans, transactions, and products. Feature snapshots are computed from these relationships.

## Design Notes

- UniqueConstraints on `(source_dataset, source_record_id)` prevent duplicate imports.
- `external_references` (JSON) stores source-specific metadata that doesn't fit the canonical schema.
- All timestamps use UTC timezone-aware datetimes.
