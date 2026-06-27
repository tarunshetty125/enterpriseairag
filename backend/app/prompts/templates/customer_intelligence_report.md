---
name: customer_intelligence_report
version: v1
description: Grounded executive customer intelligence report from ML, NLP, recommendations, and RAG evidence.
variables:
  - context
  - citations
---
You are generating an internal banking customer intelligence report.

Use only the structured evidence below. Do not invent customer facts, policies, products, or eligibility decisions.

Return a concise professional narrative with these sections: Executive Summary, Risk Assessment, Behaviour Analysis, Product Recommendations, Policy Validation, AI Summary.

Structured evidence:
{{ context }}

Policy citations:
{{ citations }}
