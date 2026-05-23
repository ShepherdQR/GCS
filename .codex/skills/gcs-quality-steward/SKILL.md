---
name: gcs-quality-steward
description: Project-specific skill for designing or reviewing GCS quality gates. Use when work touches contract tests, GTest or CTest layout, negative fixture corpora, expected reports, IO round trips, viewer projection tests, numeric robustness tests, module dependency gates, CI matrix, or regression artifacts.
---

# GCS Quality Steward

## Start Here

Use this skill for GCS test architecture and quality gates. Tests should assert
public contracts and report evidence, not current temporary implementation
details.

Read:

- `docs/architecture/62-module-agents.md` -> `Quality Agent`
- `docs/architecture/63-target-contract-interface-implementation-test-design.md`
  -> `Contract Test Architecture`
- `docs/architecture/40-quality/verification-strategy.md`
- `docs/architecture/50-implementation/third-party-policy.md`

## Workflow

1. Map the change to the module-owned contract.
2. Choose fixture class: valid, invalid, under-constrained, over-constrained,
   redundant, inconsistent, singular, gluing obstruction, IO migration, or
   viewer projection.
3. Assert structured outputs: status, report code, subject IDs, state version,
   residual evidence, and obstruction data.
4. Keep GoogleTest test-only and follow third-party policy.
5. Add CTest labels by module and risk category.

## Own

- Contract-test suite layout.
- Negative and obstruction corpora.
- Golden report snapshots.
- Dependency and CI gates.
- Test skip/failure policy.

## Refuse

- Tests coupled to private implementation internals.
- Treating skipped dependency setup as a quality pass.
- Reintroducing legacy tests as the new contract baseline.

## Required Output

Return a structured quality report with:

- contract under test;
- fixtures used or needed;
- assertions over structured reports;
- CTest labels;
- missing-test risk;
- handoffs to module or third-party stewards.
