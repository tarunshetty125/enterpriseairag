# Feature Store

The Phase 2 feature store creates deterministic, reusable customer features from canonical records.

## Feature Version

Current feature version: `features_v1`.

Every snapshot stores:

- `feature_version`
- `dataset_version`
- `generated_at`
- feature values
- feature descriptions

## Features

- Debt to income
- Savings ratio
- Spend ratio
- Credit utilization
- Salary stability
- Product count
- Loan exposure
- Average transaction amount
- Transaction frequency
- Monthly spending
- Income category
- Age group
- Customer tenure
- Risk indicators

Future ML, recommendation, and intelligence phases should consume `feature_snapshots` instead of recalculating these values independently.
