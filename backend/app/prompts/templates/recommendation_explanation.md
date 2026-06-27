---
name: recommendation_explanation
version: v1
description: Explains already-computed recommendation engine outputs.
variables: recommendation, supporting_features
---
Explain the recommendation using only the structured recommendation engine output.
Do not create new product recommendations.

Recommendation:
{{ recommendation }}

Supporting Features:
{{ supporting_features }}
