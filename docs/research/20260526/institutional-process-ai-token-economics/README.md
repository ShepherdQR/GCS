# Institutional Process AI Token Economics

Date: 2026-05-26

Audience: GCS project owner, future GCS agents, and agentic-SE governance
reviewers.

This folder contains a focused research and design bundle for the problem that
institutional/process AI tasks consume large token budgets by repeatedly
reading, rewriting, and synchronizing documents.

## Reading Order

1. [Research Report](01-research-report.md)
2. [GCS Solution Design](02-gcs-solution-design.md)
3. [Repeated Document Operations And Token Cost: Diagnosis And Operating Design](03-token-cost-diagnosis-and-operating-design.md)

## Core Thesis

The token problem is not only a pricing or context-window problem. It is a
process architecture problem.

When a repository asks an LLM to repeatedly remember policies, task cards,
sources, evidence, closure rules, role contracts, and report structure inside
the conversation, it is using expensive stochastic context as a weak process
database. The better pattern is to externalize state into small structured
artifacts, compile recurring procedures into deterministic tools, assemble
task-specific context packs, and evaluate outputs through evidence bundles.

For GCS, the next step is not to remove the lifecycle discipline. The discipline
is valuable. The next step is to make the discipline cheaper to execute:

- keep hot context tiny;
- retrieve warm context by task;
- leave cold history in indexed archives;
- turn repeated Markdown surgery into tools;
- measure token cost against validated durable output.
