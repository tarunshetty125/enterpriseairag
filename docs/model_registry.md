# Model Registry

The model registry stores metadata for every trained model version in SQLite.

## Table: `ml_model_registry`

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer (PK) | Auto-incrementing ID |
| `model_name` | String | e.g., `risk_prediction`, `customer_segmentation` |
| `version` | String | Timestamped version string |
| `algorithm` | String | e.g., `RandomForest`, `KMeans` |
| `training_date` | DateTime | When training completed |
| `metrics` | JSON | Full metrics dictionary |
| `accuracy`, `precision`, `recall`, `f1` | Float | Top-level metrics (nullable for clustering) |
| `features_used` | JSON | List of feature names |
| `artifact_path` | Text | Path to joblib file on disk |
| `dataset_version` | String | Dataset checksum at training time |
| `feature_version` | String | Feature store version |
| `active_model` | Integer | 1 = active, 0 = inactive |
| `training_time_ms` | Float | Training duration |

## Lifecycle

1. **Train** — creates a new registry entry with `active_model=0`.
2. **Evaluate** — metrics are stored at training time.
3. **Activate** — sets `active_model=1` and deactivates previous versions of the same model name.
4. **Predict** — the prediction pipeline loads the active model's artifact from disk.

Only one version per model name can be active at a time. The first trained version is auto-activated.
