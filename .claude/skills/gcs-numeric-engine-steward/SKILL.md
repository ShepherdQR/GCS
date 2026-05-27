---
name: gcs-numeric-engine-steward
description: Numeric engine contract design and review for GCS. Invoke when work touches NumericTask, local solves, residual assembly, Jacobian assembly, scaling, parameterization, manifold retraction, rank or condition estimates, boundary variables, iteration traces, or numeric failure reports.
---

# GCS Numeric Engine Steward

## Start Here

Use this skill for `gcs.numeric_engine` target design. The numeric engine
produces local sections with evidence; it never decides global acceptance.

Read:

- `docs/architecture/62-module-agents.md` -> `Numeric Engine Agent`
- `docs/architecture/63-target-contract-interface-implementation-test-design.md`
  -> `Numeric Engine Target Design`
- `docs/architecture/20-solver-pipeline/numerical-solving.md`

## Workflow

1. Define `NumericTask`, options, initial state, scaling, parameterization,
   Jacobian, linear solver, and trace policy.
2. Validate task IDs and dimensions before equation assembly.
3. Assemble residuals and Jacobians through `constraint_catalog`.
4. Report residuals, rank, condition, convergence, boundary handling, and
   iteration trace.
5. Name tests for invalid tasks, assembly dimensions, convergence, rank,
   boundary variables, and replayable traces.

## Own

- Local equation assembly.
- Numeric solve strategy within declared task boundaries.
- `LocalSection`, `NumericReport`, `ResidualReport`, `IterationTrace`.
- Rank and conditioning evidence.

## Refuse

- Cover planning, residual definitions, gluing acceptance, runtime commit.
- Hidden fallback behavior that changes mathematical meaning.

## Required Output

Return a structured design report with:

- task contract;
- solver policy;
- residual and Jacobian evidence;
- trace fields;
- failure causes;
- required tests and handoffs.

## Claude Code Integration

When invoked for numeric engine work:
- Use `Read` on architecture docs and existing numeric code before modifying
  solver strategy.
- Use `Grep` to verify that residual and Jacobian assembly routes through
  `constraint_catalog`, not ad hoc paths.
- After numeric changes, use `Bash` to run build and targeted tests:
  `scripts/build_clang_ninja.cmd` then exercise representative fixtures.
- When changing `NumericReport` or `IterationTrace` fields, `Grep` for all
  consumers of those structures.
- Numeric evidence (convergence, rank, conditioning) should be reproducible;
  record exact fixture and seed in the design report.
