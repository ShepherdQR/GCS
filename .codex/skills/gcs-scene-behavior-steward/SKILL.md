---
name: gcs-scene-behavior-steward
description: Project-specific workflow for GCS scene formats, JSON behavior models, history replay, and IO compatibility. Use when editing fixtures/scene, src/gcs/io_adapters JSON or text readers/writers, python/gcs_viz/algebra.py serialization, behavior modes, history actions, fixtures, or replay features.
---

# GCS Scene Behavior Steward

## Start Here

Use this skill whenever a change touches model persistence or replay. Read
`references/scene-behavior-contract.md` before changing C++ IO, Python
serialization, saved scenes, or history behavior.

## Format Rules

- Preserve the legacy text scene format for structural fixtures.
- Use JSON scenes for behavior intent and history. JSON must round-trip stable
  IDs, geometry parameters, constraint values, behavior fields, and history
  actions.
- Keep C++ `io_adapters` and Python `gcs_viz.algebra` schemas aligned. A scene
  saved by one side should load on the other side unless explicitly documented.
- Write deterministic output: stable field order, stable arrays, and no
  accidental loss of IDs.

## History Rules

- Treat `history` as model-embedded construction/replay data.
- Treat runtime event stores as session logs. Do not conflate them with saved
  model history.
- Record topology edits and value edits with explicit action names and payloads.
- Treat `Solve` as an action marker; replay may skip numeric solving unless the
  feature explicitly supports solve replay.

## Change Workflow

1. Identify every serializer and deserializer affected by the new field or
   action.
2. Update C++ model types, C++ IO, Python dataclasses, Python read/write
   functions, and fixtures together.
3. Add or update a saved scene fixture that exercises the changed schema.
4. Verify text compatibility still works when the change is JSON-only.
5. Verify a JSON scene can round-trip through both C++ and Python paths when
   feasible.

## Compatibility Guardrails

- Do not add a third-party C++ JSON dependency unless the user explicitly
  approves the dependency change.
- Do not make saved scenes depend on local absolute paths.
- Do not store display-only state as solver truth.
