---
task_id: 2026-05-24-step-48-replay-consumer-and-s1-03-checklist
status: complete
request: "Advance the engineering and institutional lines together: expose Step 47 runtime replay evidence through a consumer path, and turn the lifecycle into a task-to-archive checklist. Commit the scoped result."
scope: implementation
risk: high
owning_agent: gcs-session-runtime-steward
specialist_agents:
  - gcs-viewer-bridge-steward
  - gcs-cpp-solver-maintainer
  - gcs-quality-steward
  - gcs-architecture-steward
affected_contracts:
  - RuntimeReplayEvidenceExport
  - ReplayEvidenceSummary
  - SessionRuntime
  - ViewerBridge
  - GCS CLI
  - Agentic lifecycle
affected_paths:
  - src/gcs/viewer_bridge/
  - apps/gcs_cli/
  - tests/contracts/viewer_bridge/
  - tools/agentic_design/
  - docs/architecture/
  - docs/agentic/
  - docs/completed-tasks/
required_evidence:
  - validate-task-card
  - build
  - focused-viewer-bridge-tests
  - full-ctest
  - cli-replay-evidence-smoke
  - run-quality-gates
  - validate-docs
  - validate-inventory
  - check-dependencies
  - validate-completed-task-report
  - score-closure-report
human_gate_required: true
human_gate_reason: "The task touches runtime replay evidence consumption, CLI output, public quality gates, and lifecycle governance."
---

# Step 48 Replay Consumer And S1-03 Checklist

## Scope

Advance two planned tracks in one scoped closure:

- Engineering line: expose Step 47 runtime replay evidence through a public
  consumer path without changing JSON scene `history`.
- Institutional line: complete S1-03 by turning the task-card to archive loop
  into a lightweight checklist with one checked Step 47 example.

## Non-Goals

- Do not write runtime replay evidence into scene JSON `history`.
- Do not change scene IO schemas or Python saved-scene replay semantics.
- Do not change numeric, diagnostics, decomposition, or constraint semantics.
- Do not make lower solver modules depend on CLI, viewer UI policy, Python GUI,
  or agentic infrastructure.
- Do not stage or commit unrelated dirty worktree changes.

## Context To Read

- `.codex/skills/gcs-session-runtime-steward/SKILL.md`
- `.codex/skills/gcs-viewer-bridge-steward/SKILL.md`
- `.codex/skills/gcs-cpp-solver-maintainer/SKILL.md`
- `.codex/skills/gcs-quality-steward/SKILL.md`
- `.codex/skills/gcs-architecture-steward/SKILL.md`
- `docs/architecture/67-current-progress-and-next-steps.md`
- `docs/architecture/68-forward-execution-plan-2026-05-24.md`
- `docs/agentic/lifecycle-runbook.md`
- `docs/completed-tasks/2026-05-24-step-47-runtime-replay-evidence-export/README.md`

## Execution Plan

1. Add a viewer/report adapter projection over `RuntimeReplayEvidenceExport`.
2. Add a CLI flag that prints the replay evidence report for the solved command.
3. Add viewer-bridge contract coverage for the report adapter.
4. Add the CLI replay-evidence smoke to the default quality gate command list.
5. Add S1-03 task-to-archive checklist and one checked Step 47 example.
6. Update architecture and agentic roadmap docs.
7. Run focused, full, and lifecycle validation.
8. Create a completed-task archive, then stage and commit only scoped files.

## Acceptance Gates

- A public consumer can observe runtime replay evidence without private runtime
  inspection.
- The consumer path preserves `runtime_transaction_trace` report evidence and
  explicitly remains outside scene construction history.
- The default quality gate includes a replay-evidence CLI smoke.
- S1-03 has a concrete checklist and checked example.
- Completed-task archive validates and scores at or above 30.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-step-48-replay-consumer-and-s1-03-checklist.md
scripts\build_clang_ninja.cmd
ctest --test-dir out\build\clang-ninja -R "ViewerBridgeContract|SessionRuntimeContract" --output-on-failure
ctest --test-dir out\build\clang-ninja --output-on-failure
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt --replay-evidence
python tools\agentic_design\agentic_toolkit.py run-quality-gates
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-inventory
python tools\agentic_design\agentic_toolkit.py check-dependencies
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-24-step-48-replay-consumer-and-s1-03-checklist\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-24-step-48-replay-consumer-and-s1-03-checklist\README.md --min-score 30
```

## Evidence Bundle

```text
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-step-48-replay-consumer-and-s1-03-checklist.md
[OK] task-card: docs\agentic\tasks\2026-05-24-step-48-replay-consumer-and-s1-03-checklist.md passed

python -m unittest tests.tools.test_agentic_toolkit
Ran 6 tests. OK.

python tools\agentic_design\agentic_toolkit.py validate-docs
[OK] docs: module design coverage passed

python tools\agentic_design\agentic_toolkit.py validate-inventory
[OK] inventory: structured module inventory passed

scripts\build_clang_ninja.cmd
Passed after sandbox escalation for CMake build-directory write access.

ctest --test-dir out\build\clang-ninja -R "ViewerBridgeContract|SessionRuntimeContract" --output-on-failure
100% tests passed, 22 tests passed out of 22.

out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt --replay-evidence
Passed. Output included "Runtime replay evidence",
"artifact: runtime_transaction_trace", and "scene_history: false".

ctest --test-dir out\build\clang-ninja --output-on-failure
100% tests passed, 114 tests passed out of 114.

python tools\agentic_design\agentic_toolkit.py run-quality-gates
All requested quality gates passed, including ctest.public_evidence_chain
28/28 and cli.replay_evidence_basic_scene.

python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-24-step-48-replay-consumer-and-s1-03-checklist\README.md
[OK] completed-task-report: docs/completed-tasks/2026-05-24-step-48-replay-consumer-and-s1-03-checklist/README.md passed

python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-24-step-48-replay-consumer-and-s1-03-checklist\README.md --min-score 30
Closure score: 38/40.
```

## Residual Risks

- CLI text output is a report surface, not a stable scene serialization format.
- Future GUI consumption may still need a separate projection contract.
- Build and CTest needed sandbox escalation for writes under the existing build
  directory.
