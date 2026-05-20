# C++ Solver Map

## Current Layout

- `src/gcs/kernel/kernel.cppm`, `kernel.cpp`: model structs, behavior intent,
  type names.
- `src/gcs/io_adapters/io_adapters.cppm`, `io_adapters.cpp`: text and JSON
  scene read/write, summaries, graph dumping.
- `src/gcs/incidence_graph/incidence_graph.cppm`, `incidence_graph.cpp`:
  connected-component decomposition prototype.
- `src/gcs/diagnostics/diagnostics.cppm`, `diagnostics.cpp`: local geometric
  status and DOF diagnostics.
- `src/gcs/numeric_engine/numeric_engine.cppm`, `numeric_engine.cpp`:
  constraint-driven numeric solver prototype.
- `src/gcs/session_runtime/session_runtime.cppm`, `session_runtime.cpp`:
  temporary application facade.
- `apps/gcs_cli/main.cpp`: CLI executable.
- `fixtures/scene/`: reusable text and JSON scene data.

## Build

Build the CLI and solver library with:

```bat
scripts\build_clang_ninja.cmd
```

Expected executable:

```text
out/build/clang-ninja/GCS.exe
```

## Tests

The previous handwritten C++ unit tests were removed. Future tests should be
introduced as new contract-driven verification suites, not by restoring the
legacy test tree.
