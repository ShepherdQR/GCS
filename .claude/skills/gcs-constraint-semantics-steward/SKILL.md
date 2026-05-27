---
name: gcs-constraint-semantics-steward
description: Constraint semantics design and review for GCS. Invoke when work touches constraint definitions, entity signatures, parameter schemas, residual dimensions, residual evaluators, Jacobians, finite-difference checks, generic DOF metadata, degeneracy reports, or catalog versioning.
---

# GCS Constraint Semantics Steward

## Start Here

Use this skill for `gcs.constraint_catalog` target design. Current catalog code
is evidence only; derive contracts from the architecture docs.

Read:

- `docs/architecture/62-module-agents.md` -> `Constraint Semantics Agent`
- `docs/architecture/63-target-contract-interface-implementation-test-design.md`
  -> `Constraint Catalog Target Design`
- `docs/architecture/20-solver-pipeline/numerical-solving.md`
- `docs/architecture/30-contracts/solver-contracts.md`

## Workflow

1. Define each constraint through a catalog entry before numeric use.
2. Specify entity signatures, arity, parameter schema, residual dimension,
   generic DOF effect, evaluator policy, and degeneracy cases.
3. Route residual and Jacobian meaning through the catalog, not through planner
   or numeric shortcuts.
4. Require finite-difference checks for analytic Jacobians.
5. Produce tests for valid, invalid, degenerate, and evaluator-shape cases.

## Own

- `ConstraintDefinition`, `ConstraintValidationReport`.
- `ResidualEvaluationRequest`, `ResidualEvaluationResult`.
- `JacobianEvaluationRequest`, `JacobianEvaluationResult`.
- `DegeneracyReport`, `JacobianCheckReport`, catalog versioning.

## Refuse

- Ad hoc residuals in `numeric_engine`.
- Planner-specific DOF hacks when the catalog owns the semantics.
- Constraint parameters represented only as untyped scalar values.

## Required Output

Return a structured design report with:

- constraint schema;
- evaluator and Jacobian policy;
- residual dimension proof;
- degeneracy taxonomy;
- required contract tests;
- handoffs to kernel or numeric when needed.

## Claude Code Integration

When invoked for constraint catalog work:
- Use `Read` on architecture docs and existing catalog code before writing new
  constraint definitions.
- Use `Grep` with pattern `ConstraintDefinition|ResidualEvaluation` to locate
  existing constraint patterns.
- When adding a new constraint type, verify the evaluator signature matches
  existing catalog conventions via `Grep`.
- Use `Edit` for catalog entry additions; keep each entry self-contained.
- For finite-difference verification, use `Bash` to run the relevant build and
  test commands.
