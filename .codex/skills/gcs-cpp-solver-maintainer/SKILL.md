---
name: gcs-cpp-solver-maintainer
description: Project-specific workflow for maintaining the GCS C++ solver modules, CMake build, fixtures, and C++ behavior modes.
---

# GCS C++ Solver Maintainer

## Start Here

Use this skill for C++ solver work under `src/gcs/`, the CLI under
`apps/gcs_cli/`, and scene fixtures under `fixtures/scene/`. Read
`references/cpp-solver-map.md` before touching shared module boundaries.

## Module Rules

- `kernel` owns model types, stable IDs, behavior intent, and type-name helpers.
- `io_adapters` owns text and JSON scene serialization. It may print summaries,
  but solver math must not depend on file paths.
- `incidence_graph` owns current connected-subproblem structure.
- `diagnostics` owns DOF and status diagnostics.
- `numeric_engine` owns numeric solving and solve reports.
- `session_runtime` is the temporary orchestration facade. Keep executable
  policy in `apps/gcs_cli` thin.

## Change Workflow

1. Inspect the target module interface and implementation together.
2. Preserve public contracts unless the user asks for an API change. If a
   contract changes, update callers and architecture notes.
3. Use C++23 modules and the CMake/Ninja/Clang build.
4. When adding C++ files, update `CMakeLists.txt`.
5. Do not recreate the removed legacy C++ unit test tree. New verification
   should be contract-driven and designed from `docs/architecture/`.
6. Build with `scripts\build_clang_ninja.cmd` when validation is requested.

## Hard Boundaries

- Do not add browser launches, `system("start ...")`, `os.startfile`
  equivalents, or viewer side effects to solver or IO code.
- Do not make lower solver layers depend on `python/gcs_viz`, tkinter,
  matplotlib, console layout, or local build paths.
- Do not silently change mathematical meaning through fallback behavior. Return
  explicit reports or errors.
- Preserve deterministic serialization and stable IDs when editing scene IO.

## Validation

Prefer the CMake build for compile checks:

```bat
scripts\build_clang_ninja.cmd
```

Legacy C++ tests were intentionally removed during the architecture reset.
