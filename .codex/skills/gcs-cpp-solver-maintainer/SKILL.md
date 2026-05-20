---
name: gcs-cpp-solver-maintainer
description: Project-specific workflow for maintaining the GCS C++ solver modules. Use when editing src/gcs, apps/gcs_cli, CMakeLists.txt, CMakePresets.json, scripts/build_clang_ninja.cmd, C++23 module boundaries, numeric/diagnostic behavior, solver fixtures, or GCS.exe execution behavior.
---

# GCS C++ Solver Maintainer

## Start Here

Use this skill for C++ solver work under `src/gcs/`, the CLI under
`apps/gcs_cli/`, and scene fixtures under `fixtures/scene/`. Read
`references/cpp-solver-map.md` before touching shared module boundaries.

If the change affects target module boundaries, also use
`gcs-architecture-steward`. If it changes text/JSON scene IO or history fields,
also use `gcs-scene-behavior-steward`.

## Module Rules

- `kernel` owns model types, stable IDs, behavior intent, and type-name helpers.
- `io_adapters` owns text and JSON scene serialization. It may print summaries,
  but solver math must not depend on file paths.
- `incidence_graph` owns current connected-subproblem structure.
- `diagnostics` owns DOF and status diagnostics.
- `numeric_engine` owns numeric solving and solve reports.
- `session_runtime` is the temporary orchestration facade. Keep executable
  policy in `apps/gcs_cli` thin.

Do not add viewer policy, GUI dependencies, or local Python package assumptions
to these modules.

## Change Workflow

1. Inspect the target module interface and implementation together.
2. Preserve public contracts unless the user asks for an API change. If a
   contract changes, update callers and architecture notes.
3. Keep C++23 module declarations, imports, and implementation files aligned.
4. Update `CMakeLists.txt` whenever adding, renaming, or moving C++ files.
5. Preserve deterministic fixture behavior and stable IDs.
6. Do not recreate the removed legacy C++ unit test tree. New verification
   should be contract-driven and designed from `docs/architecture/`.

## Hard Boundaries

- Do not add browser launches, `system("start ...")`, `os.startfile`
  equivalents, or viewer side effects to solver or IO code.
- Do not make lower solver layers depend on `python/gcs_viz`, tkinter,
  matplotlib, console layout, or local build paths.
- Do not silently change mathematical meaning through fallback behavior. Return
  explicit reports or errors.
- Preserve deterministic serialization and stable IDs when editing scene IO.

## Validation

Use the narrowest checks that cover the change:

```bat
scripts\build_clang_ninja.cmd
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt
```

If validation touches scene compatibility, also round-trip the relevant JSON or
text scene through both C++ and Python paths where feasible. Legacy C++ tests
were intentionally removed during the architecture reset.
