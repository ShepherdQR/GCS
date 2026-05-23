---
name: gcs-viewer-bridge-steward
description: Project-specific skill for designing or reviewing GCS viewer bridge contracts. Use when work touches read-only scene projection, diagnostic overlays, selected IDs, hit-test mapping, interaction command drafts, history frame projection, viewer summaries, or GUI/API-facing report projections.
---

# GCS Viewer Bridge Steward

## Start Here

Use this skill for `gcs.viewer_bridge` target design. Viewer bridge projects
solver truth; it never owns durable truth.

Read:

- `docs/architecture/62-module-agents.md` -> `Viewer Bridge Agent`
- `docs/architecture/63-target-contract-interface-implementation-test-design.md`
  -> `Viewer Bridge Target Design`
- `docs/architecture/10-system/system-topology.md`

## Workflow

1. Define projection request fields: snapshot, reports, selected IDs, mode,
   diagnostic verbosity, and interaction intent.
2. Project stable IDs and state version into every output object.
3. Derive visual status from structured reports, not private solver guesses.
4. Draft UI interactions as runtime commands; do not mutate solver state.
5. Name tests for deterministic projection, overlays, command-draft validity,
   and history frame ID resolution.

## Own

- `ViewerSceneProjection`, `DiagnosticOverlay`.
- `InteractionCommandDraft`, `HistoryFrameProjection`.
- Selection and hit-test mapping contracts.

## Refuse

- Durable state mutation.
- Solver policy or residual interpretation.
- UI edits that bypass `session_runtime`.

## Required Output

Return a structured design report with:

- projection contracts;
- report-to-overlay mapping;
- command draft validation;
- stable ID handling;
- required viewer contract tests;
- handoffs to runtime or diagnostics.
