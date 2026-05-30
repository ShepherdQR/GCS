# C++ Module Map: Kernel And Numeric Engine Full Lane

Run id: `cpp-module-map-1-full`
Task pair: `cpp-module-map-1`
Lane: `Full`
Controller task card:
`docs/agentic/tasks/2026-05-31-cache-hit-pilot-eight-pairs.md`

## Scope

This readout maps the kernel/numeric-facing C++ module files under
`src/gcs/kernel` and `src/gcs/numeric_engine`. It uses the cache-hit pilot
runbook, architecture source-of-truth docs, and solver-maintainer module
context. It does not append `experiment-runs.csv` and does not change C++
source.

## Architecture Context Read

- `docs/research/20260530/cache-hit-diagnosis-experiment/cache-hit-rate-full-lite-pilot/pilot-runbook-8-pairs.md`
  defines this Full-lane run and acceptance gate.
- `docs/research/20260530/cache-hit-diagnosis-experiment/cache-hit-rate-full-lite-pilot/experiment-plan.md`
  defines the Full/Lite experiment scoring model and guardrails.
- `docs/architecture/README.md` names `kernel` and `numeric_engine` as target
  vocabulary.
- `docs/architecture/10-system/system-topology.md` sets dependency direction:
  `kernel` is the lowest domain layer, while `numeric_engine` depends on
  `kernel` and `constraint_catalog`.
- `docs/architecture/10-system/current-to-target-map.md` classifies
  `src/gcs/kernel` as the durable entity/contract layer and
  `src/gcs/numeric_engine` as the numeric leaf-solving prototype.
- `docs/architecture/20-solver-pipeline/numerical-solving.md` defines the
  numeric engine as a local-section producer that does not own identity,
  planning, IO, visualization, or final transaction commit.
- `docs/architecture/30-contracts/domain-contracts.md` and
  `docs/architecture/30-contracts/solver-contracts.md` define stable identity,
  snapshot/delta boundaries, `NumericTask`, and `NumericReport`.
- `.codex/skills/gcs-architecture-steward/references/architecture-map.md` and
  `.codex/skills/gcs-cpp-solver-maintainer/references/cpp-solver-map.md`
  supplied the steward map used for this Full-lane interpretation.

## Module/File List

| Path | Module role | Boundary hints |
| --- | --- | --- |
| `src/gcs/kernel/kernel.cppm` | C++23 interface for `export module gcs.kernel`. | Exports stable IDs, geometry/constraint/status enums, report/message contracts, `ModelDraft`, `ModelSnapshot`, context/cover/boundary types, `LocalSection`, `ProposedState`, `StateDelta`, validation/diff report payloads, lookup helpers, stage report helpers, context creation, snapshot creation, model validation, context validation, snapshot diff, and delta validation. |
| `src/gcs/kernel/kernel.cpp` | Implementation for `module gcs.kernel`. | Implements type-name helpers, DOF helpers, stable lookup, validation, whole-model context capture, snapshot creation, snapshot diff, and state-delta checks. It is standard-library-only and does not import other GCS modules. |
| `src/gcs/numeric_engine/numeric_engine.cppm` | C++23 interface for `export module gcs.numeric_engine`. | Re-exports `gcs.kernel` and `gcs.constraint_catalog`; exports `SolveLimits`, `NumericTask`, validation reports, residual/Jacobian assembly reports, rank/boundary/trace reports, `NumericReport`, `make_numeric_task`, `validate_task`, `assemble_equations`, and `solve_local`. |
| `src/gcs/numeric_engine/numeric_engine.cpp` | Implementation for `module gcs.numeric_engine`. | Imports `gcs.kernel` and `gcs.constraint_catalog`; validates numeric tasks, assembles residuals/Jacobians through the constraint catalog, estimates rank/condition from free Jacobian columns, freezes boundary variables, runs a dense damped Gauss-Newton baseline, and returns a local section/proposed state plus structured report. |
| `apps/gcs_cli/main.cpp` | Downstream executable consumer, not part of the mapped module pair. | Imports `gcs.io_adapters`, `gcs.session_runtime`, and `gcs.viewer_bridge`; it does not import `gcs.kernel` or `gcs.numeric_engine` directly. This supports the intended thin-shell direction through runtime/boundary modules. |
| `CMakeLists.txt` | Build registration. | Registers `kernel.cppm` and `numeric_engine.cppm` in the `CXX_MODULES` file set and `kernel.cpp`/`numeric_engine.cpp` as private sources of `gcs_solver`; also registers contract tests when GTest is available. |

## Dependency Direction Notes

- `gcs.kernel` is the bottom domain contract layer. Its implementation uses
  only standard-library headers and local declarations from its own module.
- `gcs.numeric_engine` depends upward only as expected for math execution:
  it imports `gcs.kernel` for IDs/snapshots/reports and
  `gcs.constraint_catalog` for residual/Jacobian semantics.
- The numeric engine returns proposal/report data. It does not commit durable
  state, read files, print UI text, launch processes, or call viewer/IO
  modules.
- `apps/gcs_cli/main.cpp` remains outside the lower solver pair. It calls
  runtime and boundary modules, then prints user-facing output.
- The dependency-contract test suite contains a representative forbidden-boundary
  check rejecting `gcs.kernel -> gcs.viewer_bridge`, reinforcing that lower
  solver modules must not import viewer boundaries.

## Exported Boundary Hints

- Kernel owns stable identity and snapshot-oriented contracts:
  `EntityId`, `ConstraintId`, `RigidSetId`, `ContextId`, `CoverId`,
  `ProjectionId`, `StateVersionId`, `ReportId`, `CommandId`,
  `ModelSnapshot`, `ContextSnapshot`, `BoundaryProjection`, `CoverPlan`,
  `GaugePolicy`, `LocalSection`, `ProposedState`, and `StateDelta`.
- Kernel validation is report-oriented through `StageReport`,
  `ReportMessage`, `ReportCode`, `ContractResult<T>`, and explicit validation
  report payloads.
- Numeric engine consumes immutable problem/context data through `NumericTask`
  and returns `NumericReport` with local section, proposed state, residual
  metrics, rank metrics, boundary evidence, iteration trace, result code, and
  failure cause.
- Numeric rank evidence preserves full/free/frozen dimensions, residual
  dimension, rank, nullity, under/over/singular flags, and condition estimate
  availability, matching the solver-contract requirement.

## Command Evidence

Commands run from repository root:

```powershell
Get-Content -Raw docs\agentic\tasks\2026-05-31-cache-hit-pilot-eight-pairs.md
Get-Content -Raw docs\research\20260530\cache-hit-diagnosis-experiment\pilot-runbook-8-pairs.md
Get-Content -Raw docs\research\20260530\cache-hit-diagnosis-experiment\README.md
Get-Content -Raw docs\architecture\README.md
Get-Content -Raw docs\architecture\10-system\system-topology.md
Get-Content -Raw docs\architecture\10-system\current-to-target-map.md
Get-Content -Raw docs\architecture\20-solver-pipeline\numerical-solving.md
Get-Content -Raw docs\architecture\30-contracts\domain-contracts.md
Get-Content -Raw docs\architecture\30-contracts\solver-contracts.md
rg --files src\gcs\kernel src\gcs\numeric_engine apps\gcs_cli
rg -n "^(export module|module;|module |export namespace|namespace|import )|^export (struct|class|enum|using|auto|void|double|int|bool)|^struct |^class |^enum " src\gcs\kernel src\gcs\numeric_engine apps\gcs_cli CMakeLists.txt
rg -n "system\(|start |python|matplotlib|tkinter|GCS_GUI|filesystem|fstream|cout|cerr|std::print" src\gcs\kernel src\gcs\numeric_engine apps\gcs_cli
rg -n "src/gcs/(kernel|numeric_engine)|src\\gcs\\(kernel|numeric_engine)|kernel\.cppm|numeric_engine\.cppm|numeric_engine\.cpp|kernel\.cpp" CMakeLists.txt src CMakePresets.json
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-31-cache-hit-pilot-eight-pairs.md
```

Observed evidence:

- Task-card validation passed:
  `[OK] task-card: docs/agentic/tasks/2026-05-31-cache-hit-pilot-eight-pairs.md passed`.
- File enumeration returned exactly the mapped source set:
  `src\gcs\kernel\kernel.cppm`, `src\gcs\kernel\kernel.cpp`,
  `src\gcs\numeric_engine\numeric_engine.cppm`,
  `src\gcs\numeric_engine\numeric_engine.cpp`, and downstream
  `apps\gcs_cli\main.cpp`.
- Import/module scan found `export module gcs.kernel`,
  `export module gcs.numeric_engine`, implementation modules for both, and
  `numeric_engine.cpp` importing `gcs.kernel` plus `gcs.constraint_catalog`.
- Boundary scan found console/file IO only in `apps/gcs_cli/main.cpp`; no
  `system`, GUI, Python, tkinter, matplotlib, or viewer-boundary references in
  `src/gcs/kernel` or `src/gcs/numeric_engine`.
- CMake scan confirmed both module interfaces are registered in the
  `CXX_MODULES` file set and both implementation files are private solver
  sources.

## Compile/Build Caveat

No C++ source or CMake file was changed in this run, so the acceptance check is
an auditable module map rather than a rebuild. A future code-editing run should
use `scripts\build_clang_ninja.cmd` and, where available, the contract tests
for `kernel`, `numeric_engine`, and `module_dependency`.

## Residual Risk

- This map is source-inspection based; it does not prove every transitive
  dependency policy at compile time.
- `numeric_engine.cppm` re-exports both `gcs.kernel` and
  `gcs.constraint_catalog`, which is convenient for consumers but should stay
  intentional because it broadens the module surface visible through
  `gcs.numeric_engine`.
- The current numeric engine still carries baseline dense-solver behavior and
  should be treated as a replaceable local-section backend, not as final
  global solve policy.
- Git status emitted user-config ignore permission warnings during inspection;
  this did not affect the artifact content but may obscure a clean status check
  until the local Git config path permission is repaired.

## Audit Summary

- Suggested `audit_score_0_5`: 4
- `validation_passed`: true
- `rework_turns`: 0
- `defect_or_reopen_count`: 0
- Changed files:
  - `docs/research/20260530/cache-hit-diagnosis-experiment/cache-hit-rate-full-lite-pilot/pilot-artifacts/cpp-module-map/kernel-numeric-full.md`
