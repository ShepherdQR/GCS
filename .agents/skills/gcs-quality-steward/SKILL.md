---
name: gcs-quality-steward
description: Quality gate design and review for GCS. Invoke when work touches contract tests, GTest or CTest layout, negative fixture corpora, expected reports, IO round trips, viewer projection tests, numeric robustness tests, module dependency gates, CI matrix, or regression artifacts.
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
- `docs/architecture/65-agentic-implementation-tooling.md`
- `docs/architecture/40-quality/verification-strategy.md`
- `docs/architecture/50-implementation/third-party-policy.md`

## Workflow

1. Map the change to the module-owned contract.
2. Use `python tools/agentic_design/agentic_toolkit.py scaffold-contract-test
   --module <id>` to preview contract-test placement when adding a suite.
3. Choose fixture class: valid, invalid, under-constrained, over-constrained,
   redundant, inconsistent, singular, gluing obstruction, IO migration, or
   viewer projection.
4. Assert structured outputs: status, report code, subject IDs, state version,
   residual evidence, and obstruction data.
5. Keep GoogleTest test-only and follow third-party policy.
6. Add CTest labels by module and risk category.

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

## Codex Integration

When invoked for quality gate work:
- Use `Read` on the quality architecture docs before designing new gates.
- Use `Bash` to run `python tools/agentic_design/agentic_toolkit.py scaffold-contract-test` for test placement.
- Use `Bash` for build and CTest execution after adding tests.
- Use `Grep` to verify that tests assert public contracts, not private
  implementation details.
- When designing negative tests, use `Grep` to find existing negative fixture
  patterns and follow the same conventions.
- Never mark a skipped check as a pass; record it as explicit risk.
