---
name: gcs-architecture-steward
description: Project-specific architecture guidance for GCS. Use when changing architecture docs, planning cross-module refactors, naming target modules, deciding dependency direction, or reviewing solver/runtime/IO/visualization boundaries in this repository.
---

# GCS Architecture Steward

## Start Here

Use the `docs/architecture/` tree as the source of truth for the next GCS rewrite. The current source tree is useful evidence, but it must not accidentally define the target architecture.

Read `references/architecture-map.md` first, then open only the architecture documents relevant to the requested change.

## Workflow

1. Classify the change as model, graph, planner, diagnostics, numeric engine, runtime, IO, or visualization.
2. Map current names such as `core`, `dcm`, `lgs`, `cds`, and `gcs_viz` to the target vocabulary before proposing new files or APIs.
3. Check dependency direction before coding: mathematical layers must not call UI, IO lifecycle, application singletons, file-path policy, or visualization.
4. Define or preserve contracts before implementation. Prefer stable IDs, snapshots, proposed deltas, reports, and explicit runtime commits.
5. Keep architecture docs and code mutually honest. If a code change establishes a durable rule, update the closest document under `docs/architecture/`.

## Boundary Rules

- Keep durable domain truth in kernel-like model contracts, not in the viewer.
- Keep residuals and Jacobians in constraint-catalog or numeric-engine logic, not in UI branches.
- Keep planning policy out of the numeric engine. The engine consumes tasks and returns proposals plus reports.
- Keep diagnostics able to explain under-constrained, over-constrained, redundant, inconsistent, and failed solves.
- Treat `session_runtime` as the owner of commands, transactions, history, undo, and commit/reject semantics.
- Treat `io_adapters` and `viewer_bridge` as boundary modules. They may observe and serialize, but should not mutate solver internals directly.

## Documentation Practice

Write architecture docs as durable design constraints, not as one-off implementation plans. Prefer concise contracts, data flow, invariants, and acceptance gates over historical step lists.
