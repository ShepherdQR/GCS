---
name: gcs-contract-tools-steward
description: Project-specific skill for designing or reviewing GCS contract tools. Use when work touches deterministic fixture builders, invariant checkers, corpus generation, golden report writers, module dependency audits, contract tool APIs, fixture provenance, or test-support target boundaries.
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
- `docs/architecture/40-quality/verification-strategy.md`

## Workflow

1. Define typed tool requests and reports before writing helper code.
2. Make fixture generation deterministic under explicit seed and metadata.
3. Check invariants through public contracts only.
4. Keep test-support tools in support targets, separate from production solver
   policy.
5. Name tests for deterministic generation, validation, invariant reports, and
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
