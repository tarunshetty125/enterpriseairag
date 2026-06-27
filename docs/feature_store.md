# Feature Store

The feature store creates deterministic, versioned customer features from canonical records.

## Feature Version

Current version: `features_v1`

## Features

| Feature | Type | Computation |
|---------|------|-------------|
| `age` | Integer | Direct from customer profile |
| `credit_score` | Integer | Direct from customer profile |
| `estimated_income` | Float | Direct from customer profile |
| `savings_balance` | Float | Direct from customer profile |
| `tenure_months` | Integer | Direct from customer profile |
| `total_loan_amount` | Float | Sum of loan amounts for customer |
| `product_count` | Integer | Count of products held |
| `savings_ratio` | Float | `savings_balance / estimated_income` |

## Snapshots

Feature snapshots are stored in `feature_snapshots` with composite uniqueness on `(customer_id, feature_version, dataset_version)`. This ensures:
- Each customer has one snapshot per feature version.
- Recomputing features with the same data version is idempotent.
- ML models can reference the exact feature version they were trained on.

## Usage

The feature store is consumed by:
- **ML training** — builds the feature matrix from all snapshots.
- **ML prediction** — loads a single customer's snapshot for inference.
- **Recommendation engine** — uses feature values for rule evaluation.
- **Customer Intelligence** — includes feature data in the context payload.
