# Behaviour Engine

The behaviour engine converts transaction-level NLP outputs into
customer-level behavioural intelligence.

## Inputs

- Canonical customer profile
- Canonical transactions
- Feature snapshot
- Transaction insights

## Outputs

Behaviour profiles are stored in `behaviour_profiles` and include:

- Deterministic summary
- Behaviour flags
- Lifestyle indicators
- Category spend
- Category counts
- Monthly credit/debit trends
- Top merchants
- Behaviour features
- Processing version and processing time

## Behaviour Flags

Examples:

- High Online Shopper
- Frequent Traveller
- Luxury Spending
- Medical Heavy
- Cash Dominant
- Investment Focused
- Regular Salary
- High EMI Burden
- Weekend Spender
- Irregular Income

Flags are generated only from stored data and explicit thresholds. No generated
text model is used.

## Summary Generation

The summary is deterministic template text, not AI-generated. This keeps the
result reproducible during demos and tests.

## Versioning

Profiles store `behaviour_rules_v1`. Transaction-level inputs store
`nlp_rules_v1`. These versions track which logic produced a customer profile.
