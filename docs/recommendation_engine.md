# Recommendation Engine

Phase 4 implements a deterministic, rules-based product recommendation engine.
It does not use LLMs or RAG.

## Inputs

- Customer profile
- Feature store values
- Risk level from the active Phase 3 model when available
- Segment label from the active Phase 3 model when available
- Behaviour profile
- Existing products
- Recommendation rule catalog

If active ML models are not available, the service falls back to deterministic
feature-derived risk and segment labels. This keeps the local demo functional
without retraining models automatically on startup.

## Products

The rule catalog supports:

- Credit Card
- Home Loan
- Personal Loan
- Fixed Deposit
- Mutual Fund
- SIP
- Insurance
- Savings Account Upgrade

## Scoring

Each rule has a base score and explicit conditions. The engine adjusts the score
using interpretable factors:

- Risk level match
- Income threshold
- Savings threshold
- Debt-to-income threshold
- Behaviour flags
- Customer segment
- Existing product penalties

Scores are clamped to `0-100`. Recommendations below the minimum suitability
threshold are not returned.

## Explainability

Every recommendation stores:

- Reason
- Supporting features
- Suitability score
- Confidence
- Business explanation

The explanations are derived only from the rule inputs and supporting features.
There is no hidden heuristic and no generative AI.

## Persistence

Rules are stored in `recommendation_rules`. Active generated recommendations are
stored in `recommendations`, and each generation event is recorded in
`recommendation_history`.
