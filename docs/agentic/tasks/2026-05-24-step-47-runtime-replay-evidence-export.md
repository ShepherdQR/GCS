---
task_id: 2026-05-24-step-47-runtime-replay-evidence-export
status: complete
request: "Execute Step 47 by adding deterministic runtime replay evidence export tooling without writing runtime traces into JSON scene history."
scope: implementation
risk: high
owning_agent: gcs-session-runtime-steward
specialist_agents:
  - gcs-viewer-bridge-steward
  - gcs-quality-steward
affected_contracts:
  - ReplayReport
  - HistoryEvent
  - HistoryFrameProjection
  - RuntimeReplayEvidenceExport
affected_paths:
  - src/gcs/session_runtime/
  - src/gcs/viewer_bridge/
  - tests/contracts/session_runtime/
  - tests/contracts/viewer_bridge/
  - docs/architecture/
  - docs/agentic/
required_evidence:
  - validate-task-card
  - focused-session-runtime-tests
  - focused-viewer-bridge-tests
  - build
  - ctest
  - validate-docs
  - validate-inventory
  - check-dependencies
human_gate_required: true
human_gate_reason: "High-risk runtime replay evidence boundary; user explicitly requested executing Step 47 in this session."
---

# Step 47 Runtime Replay Evidence Export

## Scope

Add a deterministic report/export surface for runtime replay evidence on top of
the Step 46 boundary. The export should package command transaction traces,
state-version evidence, artifact kind, and ordered stage evidence as runtime
reports.

The first implementation should stay in the runtime/viewer report boundary and
avoid scene persistence.

## Non-Goals

- Do not write runtime replay traces into JSON scene `history`.
- Do not change scene IO schemas or saved-scene replay semantics.
- Do not add a third-party dependency.
- Do not change numeric, diagnostics, decomposition, or constraint semantics.
- Do not make lower solver modules depend on viewer, IO, CLI, Python GUI, or
  agentic infrastructure.
- Do not run the `裁缝` timeline role for this lifecycle sample.

## Context To Read

- `.codex/skills/gcs-session-runtime-steward/SKILL.md`
- `.codex/skills/gcs-cpp-solver-maintainer/SKILL.md`
- `.codex/skills/gcs-scene-behavior-steward/SKILL.md`
- `docs/architecture/66-implementation-execution-roadmap.md`
- `docs/architecture/67-current-progress-and-next-steps.md`
- `docs/architecture/68-forward-execution-plan-2026-05-24.md`
- `src/gcs/session_runtime/session_runtime.cppm`
- `src/gcs/session_runtime/session_runtime.cpp`
- `src/gcs/viewer_bridge/viewer_bridge.cppm`
- `src/gcs/viewer_bridge/viewer_bridge.cpp`
- `tests/contracts/session_runtime/session_runtime_contract_tests.cpp`
- `tests/contracts/viewer_bridge/viewer_bridge_contract_tests.cpp`

## Execution Plan

### Base Context

- Architecture docs read: Step 46 and Step 47 roadmap sections.
- Skills read: session runtime, C++ solver maintainer, scene behavior.
- Source files to inspect: session runtime and viewer bridge interfaces and
  tests.
- Fixture or tests to inspect: existing replay boundary contract tests.

### Ownership

- Owning boundary: `gcs.session_runtime`.
- Specialist boundary: `gcs.viewer_bridge` only if history-frame export
  projection is needed.
- Refused boundary: `gcs.io_adapters` scene JSON `history`.
- Dependency direction impact: runtime must not depend on IO, viewer, CLI,
  Python, or agentic infrastructure.

### Step Plan

1. Define compact runtime replay evidence export DTOs in
   `gcs.session_runtime`.
2. Add a deterministic export method that derives the report from stored
   runtime history.
3. Preserve missing-command behavior with typed runtime report evidence.
4. Add session-runtime contract tests for deterministic export shape,
   stage ordering, missing command behavior, and scene-history separation.
5. Add viewer-bridge projection tests only if the export needs viewer-facing
   frame evidence in this step.
6. Update architecture progress docs and roadmap after verification.
7. Close with a completed-task archive and a `刀匠` experience-forging note.

## Acceptance Gates

- Runtime replay evidence can be exported deterministically for a stored
  command.
- Export includes command ID, artifact kind, report-evidence flag,
  state-version range, command status, ordered stages, and stable report codes.
- Missing command export returns a deterministic rejected/missing report.
- Runtime replay export remains report evidence and is not scene construction
  history.
- Focused contract tests pass.
- Required agentic docs validation passes or skipped checks are recorded.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-step-47-runtime-replay-evidence-export.md
scripts\build_clang_ninja.cmd
ctest --test-dir out\build\clang-ninja --output-on-failure
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-inventory
python tools\agentic_design\agentic_toolkit.py check-dependencies
```

## Evidence Bundle

```text
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-step-47-runtime-replay-evidence-export.md
[OK] task-card: docs\agentic\tasks\2026-05-24-step-47-runtime-replay-evidence-export.md passed

scripts\build_clang_ninja.cmd
Passed after sandbox escalation for CMake pkgRedirects write access.

python tools\agentic_design\agentic_toolkit.py validate-docs
[OK] docs: module design coverage passed

python tools\agentic_design\agentic_toolkit.py validate-inventory
[OK] inventory: structured module inventory passed

python tools\agentic_design\agentic_toolkit.py check-dependencies
[OK] dependencies: import boundaries passed

ctest --test-dir out\build\clang-ninja -R "SessionRuntimeContract|ViewerBridgeContract" --output-on-failure
100% tests passed, 21 tests passed out of 21.

ctest --test-dir out\build\clang-ninja --output-on-failure
100% tests passed, 113 tests passed out of 113.

out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt
Passed CLI smoke; runtime accepted the basic scene with existing warning output.

python tools\agentic_design\agentic_toolkit.py run-quality-gates
All requested quality gates passed after sandbox escalation for build output access.

python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-24-step-47-runtime-replay-evidence-export\README.md
[OK] completed-task-report: docs/completed-tasks/2026-05-24-step-47-runtime-replay-evidence-export/README.md passed

python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-24-step-47-runtime-replay-evidence-export\README.md --min-score 30
Closure score: 37/40 for docs/completed-tasks/2026-05-24-step-47-runtime-replay-evidence-export/README.md
```

## Residual Risks

- The first export surface is runtime API only; CLI, GUI, or report-adapter
  consumption is registered as Step 48.
- If existing dirty worktree changes touch quality gates, full-gate evidence
  may need to record unrelated failures rather than edit unrelated files.
- The `裁缝` timeline role was intentionally skipped for this lifecycle sample
  per the user request.
