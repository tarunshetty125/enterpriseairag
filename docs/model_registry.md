# Model Registry

The model registry stores metadata for every trained model version in SQLite.

## Table

`ml_model_registry`

Tracked fields:

- Model name
- Version
- Algorithm
- Training date
- Accuracy
- Precision
- Recall
- F1
- Full metrics payload
- Features used
- Artifact path
- Dataset version
- Feature version
- Active model flag
- Training time
- Latest inference time
- Training metadata

## Active Models

Only one active version is allowed per model name. Registering a new version
automatically deactivates older versions of the same model. The UI can also
activate a previous version through the registry endpoint.

## Prediction Logs

`ml_prediction_logs` records local inference calls with customer ID, model
version, prediction, confidence, and inference latency. These counts feed the
developer console and ML dashboard.
