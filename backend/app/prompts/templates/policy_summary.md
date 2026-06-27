---
name: policy_summary
version: v1
description: Summarizes retrieved policy excerpts without adding new rules.
variables: context, citations
---
Summarize the retrieved financial policy excerpts.
Use only the provided context and include citations.

Context:
{{ context }}

Citations:
{{ citations }}
