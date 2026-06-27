# Explainability

The platform uses model-native feature importance for explainability. Every prediction and recommendation includes structured evidence.

## Risk Explanations

Risk predictions return:
- **Feature importance** — ranked list from `RandomForestClassifier.feature_importances_`.
- **Individual feature values** — the customer's actual values for each feature.
- **Confidence score** — the model's probability for the predicted class.
- **Risk level mapping** — Low / Medium / High derived from confidence thresholds.

## Recommendation Explanations

Each recommendation includes:
- **Reason** — human-readable explanation of why the product was recommended.
- **Supporting features** — list of features with their values and impact scores.
- **Suitability score** — composite score (0-100) from rule evaluation.
- **Business explanation** — narrative explanation derived from rule conditions.

## Intelligence Report Evidence

The Customer Intelligence Report exposes:
- ML predictions with feature importance drivers.
- Behaviour profile flags and lifestyle indicators.
- Recommendation reasons with supporting features.
- Retrieved policy chunks with similarity scores.
- Citations linking to source documents.
- Token usage, latency, and provider metadata.
- Full workflow trace with per-stage timing.

## Design Choice

The platform uses model-native importance rather than post-hoc methods like SHAP or LIME. This keeps the demo fast, dependency-light, and easy to explain. Adding SHAP is listed as a future improvement.
