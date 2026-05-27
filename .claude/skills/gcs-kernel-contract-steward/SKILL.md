---
name: gcs-kernel-contract-steward
description: Kernel contract design and review for GCS. Invoke when work touches stable IDs, immutable ModelSnapshot, ContextSnapshot, StateDelta, units, tolerances, report codes, model validation, context validation, snapshot diffing, or state-version semantics.
---

# GCS Kernel Contract Steward

## Start Here

Use this skill for `gcs.kernel` target design. Treat current C++ files as
temporary scaffolding, not the baseline.

Read only the relevant sections first:

- `docs/architecture/62-module-agents.md` -> `Kernel Contract Agent`
- `docs/architecture/63-target-contract-interface-implementation-test-design.md`
  -> `Kernel Target Design`
- `docs/architecture/30-contracts/domain-contracts.md`
- `docs/architecture/30-contracts/solver-contracts.md`

## Workflow

1. Identify whether the change touches identity, snapshots, contexts, policies,
   reports, or state transitions.
2. Define structured inputs and outputs before implementation names.
3. Keep durable truth in kernel contracts: stable IDs, immutable snapshots,
   explicit contexts, typed reports, and versioned deltas.
4. Specify report codes and subject IDs for every invalid case.
5. Name contract tests that import public C++23 modules only.

## Own

- `ModelDraft`, `ModelSnapshot`, `ContextRequest`, `ContextSnapshot`.
- `StateDelta`, `SnapshotDiff`, validation reports, report-code registry.
- Stable ID allocation and duplicate detection.
- Unit, tolerance, parameter dimension, rigid-set, and context validation.

## Refuse

- Solver strategy, residuals, Jacobians, planner policy, numeric iteration.
- IO paths, CLI formatting, GUI state, viewer policy, or Python assumptions.
- Coordinate mutation without explicit state-version transition.

## Required Output

Return a structured design report with:

- contracts added or changed;
- invariants protected;
- report codes and subjects;
- required contract tests;
- affected downstream modules;
- residual risks.

## Claude Code Integration

When invoked for kernel contract work:
- Use `Read` on the architecture docs listed above before proposing contract
  changes.
- Use `Grep` to find all callers of a contract before changing its signature.
- Use `Edit` for surgical contract updates; preserve surrounding invariants.
- When adding report codes, `Grep` for existing codes to avoid collisions.
- Use `Agent` with subagent_type="Explore" to verify that no downstream module
  silently depends on the contract being changed.
