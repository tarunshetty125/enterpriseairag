# Explainability

Phase 3 uses model-native feature importance for explainability.

## Risk Explanations

The Random Forest artifact stores feature importances sorted by contribution.
Prediction responses include:

- Risk level
- Confidence
- Class probabilities
- Top model features
- Feature values
- Business explanation

The business explanation is generated only from feature names, feature values,
and model importances. It does not infer unsupported causes.

Example:

`The model predicted High risk because the highest-weighted features for this customer were high debt to income, low savings ratio, and low credit score.`

## Segmentation Explanations

KMeans predictions return:

- Business segment label
- Confidence derived from distance to centroids
- Nearest centroid distance
- Centroid feature summary

Cluster numbers remain internal.
