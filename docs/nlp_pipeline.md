# NLP Pipeline

The NLP layer implements deterministic transaction intelligence. It uses
rules-based classification, pattern matching, and keyword analysis — no
LLMs, external NLP models, or API calls.

## Pipeline

```text
Raw Transaction Description
  -> Cleaning
  -> Normalization
  -> Keyword Extraction
  -> Entity Extraction
  -> Category Classification
  -> Sentiment Signal
  -> Lifestyle Indicators
  -> transaction_insights
```

## Classification Strategy

The transaction classifier combines normalized text keywords with canonical
transaction metadata. Keyword matches are applied first because they are easier
to explain in a demo. If no keyword is found, deterministic fallbacks use
transaction type and amount bands.

Supported categories include:

- Salary
- Shopping
- Food
- Travel
- Fuel
- Medical
- ATM
- Bills
- Investment
- Insurance
- Entertainment
- Education
- Loan
- Transfer
- Miscellaneous

Each persisted insight stores the classification reason in `entities` so the UI
can explain why the category was assigned.

## Entity Extraction

The entity extractor identifies merchant, institution, brand, payment type,
counterparty, and coarse location when those values are present in the
transaction text or canonical fields.

This approach is intentionally rule-assisted. It is reproducible, testable, and
sufficient for an interview system without adding model downloads or runtime
complexity.

## Sentiment

Sentiment is a lightweight deterministic signal. It uses transaction direction,
category, fraud flags, and a small financial lexicon. The result is stored as a
label and numeric score.

## Persistence

Outputs are stored in `transaction_insights`. The table is idempotent by
`transaction_id`, so rerunning the pipeline updates existing records instead of
creating duplicates.
