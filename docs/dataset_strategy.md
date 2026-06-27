# Dataset Strategy

The platform uses public Kaggle datasets only. Raw files are kept immutable in `data/raw/`.

## Sources

| Dataset | File | Records | Purpose |
|---------|------|---------|---------|
| Bank Customer Churn | `bank_customer_churn.csv` | ~10,000 | Demographics, credit scores, churn labels |
| Credit Card Customers | `credit_card_customers.csv` | ~10,000 | Products, credit limits, balances |
| Loan Prediction | `loan_prediction.csv` | ~600 | Loan applications, approval status |
| PaySim Transactions | `paysim_transactions_sample.csv` | ~2,500 | Simulated transaction descriptions |

## Ingestion Pipeline

```text
Raw CSV → Loader → Validator → Mapper → Normalizer → Linker → Seeder → SQLite
```

1. **Loader** — reads CSV files from `data/raw/`.
2. **Validator** — checks required columns, types, and value ranges.
3. **Mapper** — maps source columns to canonical schema fields.
4. **Normalizer** — standardizes values (e.g., gender, geography, income bands).
5. **Linker** — generates deterministic customer IDs via hashing (see `synthetic_join_strategy.md`).
6. **Seeder** — inserts canonical records into SQLite tables.

Ingestion is idempotent. Running `POST /datasets/ingest` again updates existing records.

## Data Quality

A quality report (`GET /data-quality`) checks:
- Completeness (null rates per column)
- Uniqueness (duplicate detection)
- Value distribution anomalies
- Cross-table referential integrity
