---
name: gcs-decomposition-planning-steward
description: Project-specific skill for designing or reviewing GCS decomposition planning. Use when work touches context covers, overlap contexts, BoundaryProjection, GaugePolicy, subproblems, SolveDag, coverage proofs, unsupported plan reports, rigidity hints, separator planning, or local-to-global solve ordering.
---

# GCS Decomposition Planning Steward

## Start Here

Use this skill for `gcs.decomposition_planner` target design. Planning chooses
the cover and schedule; it does not solve equations or commit state.

Read:

- `docs/architecture/62-module-agents.md` -> `Decomposition Planning Agent`
- `docs/architecture/63-target-contract-interface-implementation-test-design.md`
  -> `Decomposition Planner Target Design`
- `docs/architecture/00-foundations/topos-semantic-model.md`
- `docs/architecture/20-solver-pipeline/decomposition-planning.md`

## Workflow

1. Start from requested solve scope, incidence indices, and hints.
2. Define `PlanningRequest`, `CoverPlan`, contexts, overlaps, boundary
   projections, gauge policy, subproblems, and solve DAG.
3. Prove coverage and overlap validity through structured reports.
4. Return `UnsupportedPlanReport` instead of hidden fallback behavior.
5. Name contract tests for coverage, boundary projections, DAG validity, gauge,
   deterministic output, and unsupported cases.

## Own

- Cover selection and validation.
- `BoundaryProjection` construction.
- Explicit gauge policy.
- `SolveDag` and fallback/unsupported reports.

## Refuse

- Residual evaluation, numeric iteration, diagnostics acceptance, state commit.
- Covers that omit requested IDs or hide shared boundary variables.

## Required Output

Return a structured design report with:

- planning contracts;
- coverage proof;
- boundary and gauge rationale;
- dependency DAG proof;
- unsupported-case evidence;
- required tests and handoffs.
