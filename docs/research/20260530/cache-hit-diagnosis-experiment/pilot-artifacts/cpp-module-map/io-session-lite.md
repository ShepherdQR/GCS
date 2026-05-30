# IO/Session C++ Module Map Lite

Task pair: `cpp-module-map-1`
Lane: `lite`
Controller task card: `docs/agentic/tasks/2026-05-31-cache-hit-pilot-eight-pairs.md`

## Module/File List

Observed C++ module pairs under `src/gcs/`:

- `src/gcs/io_adapters/io_adapters.cppm`
- `src/gcs/io_adapters/io_adapters.cpp`
- `src/gcs/session_runtime/session_runtime.cppm`
- `src/gcs/session_runtime/session_runtime.cpp`

Adjacent files that directly consume the IO/session boundary:

- `apps/gcs_cli/main.cpp`
- `src/gcs/viewer_bridge/viewer_bridge.cppm`
- `src/gcs/viewer_bridge/viewer_bridge.cpp`
- `tests/contracts/io_adapters/io_adapters_contract_tests.cpp`
- `tests/contracts/session_runtime/session_runtime_contract_tests.cpp`

`CMakeLists.txt` registers both `io_adapters` and `session_runtime` module
interfaces and implementations in the main `gcs_core` source list, then defines
separate contract test executables for each module.

## Ownership And Dependency Signals

- `gcs.io_adapters` exports kernel-facing scene IO contracts: schema registry,
  load/write requests and results, parse issues, migration reports, canonical
  text/JSON serialization, digesting, round-trip reports, and scene summaries.
- `gcs.io_adapters` imports only `gcs.kernel` in the inspected module files.
  This makes IO a boundary adapter over `ModelSnapshot`, stable IDs,
  `StageReport`, and kernel validation rather than an orchestration owner.
- `gcs.session_runtime` exports command, validation, transaction trace,
  rollback, history, replay, replay-evidence export, rank-evidence projection,
  and `SessionRuntime`.
- `gcs.session_runtime` imports `gcs.kernel`, `gcs.constraint_catalog`,
  `gcs.incidence_graph`, `gcs.decomposition_planner`, `gcs.numeric_engine`, and
  `gcs.diagnostics`. It does not import `gcs.io_adapters` in the inspected
  files, so file/schema policy remains outside runtime orchestration.
- `apps/gcs_cli/main.cpp` is the visible IO/session composition point: it imports
  `gcs.io_adapters` and `gcs.session_runtime`, loads a scene with
  `gcs::io::load_scene`, constructs `gcs::runtime::SessionRuntime`, solves, and
  optionally exports replay evidence.
- `viewer_bridge` imports and re-exports session runtime, signaling read-only
  presentation/report projection over runtime results rather than ownership of
  runtime commit semantics.

## Compact Readout

The IO/session split is clear in the current C++ module surface. IO adapts files
to kernel snapshots and deterministic bytes; session runtime coordinates solver
modules against an in-memory snapshot and records transaction/replay evidence.
The CLI currently stitches the two together. No obvious lower-layer dependency
from session runtime back into IO was found in the minimal scan.

## Command Evidence

```powershell
Get-Content docs\agentic\tasks\2026-05-31-cache-hit-pilot-eight-pairs.md -TotalCount 200
Get-ChildItem src\gcs -Recurse -File | Select-Object -ExpandProperty FullName
Get-Content src\gcs\io_adapters\io_adapters.cppm
Get-Content src\gcs\io_adapters\io_adapters.cpp
Get-Content src\gcs\session_runtime\session_runtime.cppm
Get-Content src\gcs\session_runtime\session_runtime.cpp
Select-String -Path CMakeLists.txt -Pattern "io_adapters|session_runtime|src/gcs" -Context 1,1
Select-String -Path apps\gcs_cli\* -Pattern "import gcs\.io_adapters|import gcs\.session_runtime|gcs::io|gcs::runtime" -Context 2,2
Select-String -Path tests\contracts\io_adapters\*.cpp,tests\contracts\session_runtime\*.cpp -Pattern "import gcs\.|TEST|TEST_F" -Context 0,1
Select-String -Path src\gcs\*\*.cppm,src\gcs\*\*.cpp -Pattern "import gcs\.io_adapters|import gcs\.session_runtime|export import gcs\.io_adapters|export import gcs\.session_runtime"
```
