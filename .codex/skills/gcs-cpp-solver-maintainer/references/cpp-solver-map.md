# C++ Solver Map

## Current Layout

- `GCS/core/core.h`, `core.cpp`, `types.h`: model structs, behavior intent, type names.
- `GCS/io/io.h`, `io.cpp`: text and JSON scene read/write, summaries, graph dumping.
- `GCS/dcm/dcm.h`, `dcm.cpp`: decomposition manager.
- `GCS/lgs/lgs.h`, `lgs.cpp`: local geometric status and DOF diagnostics.
- `GCS/cds/cds.h`, `cds.cpp`: constraint-driven numeric solver.
- `GCS/app/App.h`, `App.cpp`, `main.cpp`: application facade and demo executable.
- `GCS/test/`: custom C++ test executables and fixtures.
- `GCS/scene/`: reusable text and JSON scene data.

## Tests

- Build tests with `GCS\test\build_tests.bat`.
- Run tests with `GCS\test\run_tests.bat`.
- Expected executables are under `build\bin\x64\Debug`.

## Project Files

When adding source or header files, update:

- `GCS/GCS.vcxproj`
- `GCS/GCS.vcxproj.filters`

Keep include paths compatible with the existing commands in `build_tests.bat`, which compile from the `GCS/` directory with `/I"." /I"test"`.
