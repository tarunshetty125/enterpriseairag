# Training Pipeline

## Risk Prediction

```text
Feature Store → Feature Matrix Builder → StandardScaler → RandomForestClassifier → Evaluate → Save Artifact → Register
```

1. Load all feature snapshots from SQLite.
2. Build the feature matrix (8 features) and derive the target label from churn/attrition flags.
3. Split 80/20 train/test.
4. Scale features with `StandardScaler`.
5. Train a `RandomForestClassifier`.
6. Evaluate: accuracy, precision, recall, F1.
7. Save the model + scaler as a versioned joblib artifact under `models/risk_prediction/`.
8. Register in `ml_model_registry` with metrics, feature list, and artifact path.

## Customer Segmentation

```text
Feature Store → Feature Matrix Builder → StandardScaler → KMeans → Evaluate → Save Artifact → Register
```

Same pipeline as risk prediction, except:
- Uses `KMeans` clustering instead of classification.
- Evaluates with silhouette score and inertia.
- Cluster labels are mapped to descriptive segment names (e.g., "High Value", "At Risk").
- Artifacts saved under `models/customer_segmentation/`.

## Versioning

Each training run creates a timestamped version string (e.g., `risk_20260626193002`). The registry supports multiple versions per model name. Only one version is active at a time; activation is explicit via `POST /ml/models/{id}/activate`.

## Artifacts

Model artifacts are stored as joblib files containing the fitted model and scaler. The artifact path is recorded in the registry so the prediction pipeline can load the correct version.
