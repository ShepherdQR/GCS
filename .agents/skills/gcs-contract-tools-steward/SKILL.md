---
name: gcs-contract-tools-steward
description: Contract tools design and review for GCS. Invoke when work touches deterministic fixture builders, invariant checkers, corpus generation, golden report writers, module dependency audits, contract tool APIs, fixture provenance, or test-support target boundaries.
---

# GCS Contract Tools Steward

## Start Here

Use this skill for `gcs.contract_tools` and support tooling. Contract tools
turn architecture claims into reproducible fixtures and audits; they do not
define production solver policy.

Read:

- `docs/architecture/62-module-agents.md` -> `Contract Tools Agent`
- `docs/architecture/63-target-contract-interface-implementation-test-design.md`
  -> `Contract Tools Target Design`
- `docs/architecture/65-agentic-implementation-tooling.md`
- `docs/architecture/40-quality/verification-strategy.md`

## Workflow

1. Run `python tools/agentic_design/agentic_toolkit.py validate-docs` before
   changing module contract scaffolding.
2. Define typed tool requests and reports before writing helper code.
3. Make fixture generation deterministic under explicit seed and metadata.
4. Check invariants through public contracts only.
5. Keep test-support tools in support targets, separate from production solver
   policy.
6. Name tests for deterministic generation, validation, invariant reports, and
   dependency audits.

## Own

- `FixtureBuildRequest`, `InvariantCheckRequest`, `CorpusGenerationRequest`.
- `GoldenReportRequest`, `DependencyAuditRequest`.
- Fixture provenance and module dependency reports.

## Refuse

- Hidden production solver policy in test helpers.
- Nondeterministic fixtures without explicit seed.
- Tests that require private implementation access.

## Required Output

Return a structured design report with:

- tool input and output contracts;
- fixture provenance;
- deterministic replay steps;
- target boundary impact;
- required tests;
- handoffs to quality or module stewards.

## Codex Integration

When invoked for contract tools work:
- Use `Bash` to run `python tools/agentic_design/agentic_toolkit.py validate-docs` before modifying scaffolding.
- Use `Bash` to run the agentic toolkit commands for task cards, validation,
  and scoring.
- Use `Grep` to verify that test-support tools don't leak into production
  solver targets.
- When building fixtures, use explicit seeds and record them in fixture
  metadata.
- Use `Edit` for tool API changes; keep tool contracts typed and documented.
