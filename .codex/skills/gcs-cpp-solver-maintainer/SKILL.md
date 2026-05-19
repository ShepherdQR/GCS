---
name: gcs-cpp-solver-maintainer
description: Project-specific workflow for maintaining the GCS C++ solver and tests. Use when editing GCS/core, GCS/io, GCS/dcm, GCS/lgs, GCS/cds, GCS/app, GCS/test, Visual Studio project files, solver fixtures, or C++ behavior modes.
---

# GCS C++ Solver Maintainer

## Start Here

Use this skill for C++ solver work in `GCS/`. Read `references/cpp-solver-map.md` before touching shared module boundaries or tests.

## Module Rules

- `core` owns model types, stable IDs, behavior intent, and type-name helpers.
- `io` owns text and JSON scene serialization. It may print summaries, but solver math must not depend on file paths.
- `dcm` owns decomposition and connected subproblem structure.
- `lgs` owns DOF and status diagnostics.
- `cds` owns numeric solving and solve reports.
- `app` is a facade and demo entry point. It orchestrates modules; it should not hide solver policy in UI or IO helpers.

## Change Workflow

1. Inspect the target header and implementation together, plus the closest tests under `GCS/test/`.
2. Preserve public contracts unless the user asks for an API change. If a contract changes, update callers, tests, and architecture notes.
3. Keep C++17 compatibility and the existing flat module layout (`GCS/<module>/<module>.h`, `GCS/<module>/<module>.cpp`).
4. When adding C++ files, update both `GCS/GCS.vcxproj` and `GCS/GCS.vcxproj.filters`.
5. Add or update the smallest useful test for the changed module. For cross-module behavior, prefer an app or pipeline test fixture.
6. Run the relevant batch build/test commands when Visual Studio tools are available.

## Hard Boundaries

- Do not add browser launches, `system("start ...")`, `os.startfile` equivalents, or viewer side effects to solver or IO code.
- Do not make lower solver layers depend on `gcs_viz`, tkinter, matplotlib, console layout, or local build paths.
- Do not silently change mathematical meaning through fallback behavior. Return explicit reports or errors.
- Preserve deterministic serialization and stable IDs when editing scene IO.

## Validation

Prefer focused checks first, then broader checks:

```bat
GCS\test\build_tests.bat
GCS\test\run_tests.bat
```

If those cannot run in the current shell, still inspect compile-sensitive files and report the unrun validation clearly.
