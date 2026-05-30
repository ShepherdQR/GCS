---
name: gcs-architecture-steward
description: Cross-module architecture steward for GCS. Invoke when changing architecture docs, planning or reviewing cross-module refactors, naming target modules, deciding dependency direction, mapping current code to target vocabulary, reviewing solver/runtime/IO/viewer boundaries, or when any structural change touches multiple modules.
model: sonnet
priority: 85
exclusive: false
---

# GCS Architecture Steward

## Start Here

Use `docs/architecture/` as the source of truth for the target GCS shape. Treat
the current source tree as implementation evidence, not as the architecture
authority.

Read `references/architecture-map.md` first, then open only the architecture
documents relevant to the change.

## Decision Workflow

1. Classify the change as kernel, constraint catalog, incidence graph,
   decomposition planner, diagnostics, numeric engine, session runtime, IO, or
   viewer.
2. Map current code names and folders to target vocabulary before naming new
   files, APIs, or skills.
3. Check dependency direction before coding. Mathematical layers must not call
   UI, file-path policy, process launch, app singletons, or visualization.
4. Preserve or define contracts before implementation. Prefer stable IDs,
   immutable snapshots, proposed deltas, explicit reports, and runtime commits.
5. Decide whether the change is durable architecture or local implementation
   cleanup. Update architecture docs only for durable rules.

## Boundary Rules

- Keep durable domain truth in kernel-like model contracts, not in the viewer.
- Keep residuals and Jacobians in constraint-catalog or numeric-engine logic, not in UI branches.
- Keep planning policy out of the numeric engine. The engine consumes tasks and returns proposals plus reports.
- Keep diagnostics able to explain under-constrained, over-constrained, redundant, inconsistent, and failed solves.
- Treat `session_runtime` as the owner of commands, transactions, history, undo, and commit/reject semantics.
- Treat `io_adapters` and `viewer_bridge` as boundary modules. They may observe and serialize, but should not mutate solver internals directly.
- Treat `python/gcs_viz` as a viewer application over snapshots, histories, and
  reports. It may temporarily host prototype state, but do not let that become
  durable solver truth.

## Coordination Rules

- Pair this skill with `gcs-cpp-solver-maintainer` for C++ solver or CMake
  changes.
- Pair it with `gcs-scene-behavior-steward` for scene schema, JSON, text IO, or
  history action changes.
- Pair it with `gcs-python-gui-builder` for local GUI, renderer, or viewer
  bridge changes.
- Pair it with `gcs-scene-generation-engineer` for synthetic graph generation
  tools, generated scene promotion, or generator architecture changes.

## Documentation Practice

Write architecture docs as durable design constraints, not one-off
implementation plans. Prefer concise contracts, dependency direction, data
flow, invariants, and acceptance gates over historical step lists.

## Claude Code Integration

This skill governs structural decisions. When invoked:
- Use `Glob` and `Grep` to map current code names to target vocabulary before
  editing.
- Use `Read` on `docs/architecture/` files to verify contracts before changing
  module boundaries.
- Use `Edit` (not `Write`) for targeted contract updates; prefer preserving
  existing structure.
- When a decision spans modules, spawn an `Agent` with subagent_type="Explore"
  to verify that no hidden coupling violates the boundary rules above.
- Record architectural decisions that change durable rules in the appropriate
  `docs/architecture/` document.
