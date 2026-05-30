---
name: gcs-scene-behavior-steward
description: Scene format, JSON behavior, history replay, and IO compatibility for GCS. Invoke when editing fixtures/scene, io_adapters JSON or text readers/writers, python/gcs_viz/algebra.py serialization, behavior modes, history actions, saved scenes, replay reconstruction, or scene compatibility fixtures.
---

# GCS Scene Behavior Steward

## Start Here

Use this skill whenever a change touches model persistence or replay. Read
`references/scene-behavior-contract.md` before changing C++ IO, Python
serialization, saved scenes, or history behavior.

If the change is C++ implementation work, also use
`gcs-cpp-solver-maintainer`. If it changes GUI replay UX, also use
`gcs-python-gui-builder`. If it changes the durable ownership of commands,
history, or IO, also use `gcs-architecture-steward`. If a generated scene is
being created, validated, repaired, or promoted from `tools/scene_generation`,
also use `gcs-scene-generation-engineer`.

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
- Replayers should tolerate unknown future actions by skipping or surfacing a
  non-fatal warning, not by corrupting the reconstructed graph.

## Change Workflow

1. Identify every serializer and deserializer affected by the new field or
   action.
2. Update C++ model types, C++ IO, Python dataclasses, Python read/write
   functions, and fixtures together.
3. Add or update a saved scene fixture that exercises the changed schema.
4. Verify text compatibility still works when the change is JSON-only.
5. Verify a JSON scene can round-trip through both C++ and Python paths when
   feasible.
6. Keep runtime event logs separate from model-embedded `history`.

## Compatibility Guardrails

- Do not add a third-party C++ JSON dependency unless the user explicitly
  approves the dependency change.
- Do not make saved scenes depend on local absolute paths.
- Do not store display-only state as solver truth.

## Validation

Use targeted checks for the affected path:

```bat
python -m compileall -q python\gcs_viz
scripts\build_clang_ninja.cmd
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt
```

When possible, load and save a representative JSON fixture and inspect that
stable IDs, behavior, constraints, values, and `history` survive unchanged.

## Codex Integration

When invoked for scene behavior work:
- Use `Grep` to identify every serializer and deserializer affected before
  making changes.
- Use `Edit` to update C++ IO, Python dataclasses, and fixtures in lockstep.
- Use `Bash` for build verification and round-trip testing.
- When adding a new field, use `Agent` with subagent_type="Explore" to find all
  code paths that read or write the parent structure.
- Keep validation output visible; use `Bash` to run the exact commands listed
  above and share results.
