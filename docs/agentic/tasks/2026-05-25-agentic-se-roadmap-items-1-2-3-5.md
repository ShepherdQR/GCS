---
task_id: 2026-05-25-agentic-se-roadmap-items-1-2-3-5
status: complete
request: "Execute roadmap items 1, 2, 3, and 5 while leaving item 4 to the parallel session."
scope: tool
risk: medium
owning_agent: gcs-quality-steward
specialist_agents:
  - gcs-scene-generation-engineer
  - gcs-ui-design-steward
affected_contracts:
  - Agentic artifact opt-in quality gates
  - Promoted scene fixture-library gate
  - Institutional visual seed-agent packages
affected_paths:
  - tools/agentic_design/agentic_toolkit.py
  - tests/tools/test_agentic_toolkit.py
  - tools/scene_generation/fixture_library_gate.py
  - tests/tools/test_fixture_library_gate.py
  - docs/agentic/
  - docs/architecture/
required_evidence:
  - python -m unittest tests.tools.test_agentic_toolkit
  - python -m unittest tests.tools.test_fixture_library_gate
  - python tools/scene_generation/fixture_library_gate.py --gcs-exe out/build/clang-ninja/GCS.exe
  - validate-task-card
  - validate-completed-task-report
  - score-closure-report
  - run-quality-gates opt-in artifact/fixture selection
  - validate-docs
human_gate_required: false
human_gate_reason: ""
---

# Agentic SE Roadmap Items 1, 2, 3, And 5

## Scope

Execute the next Agentic SE roadmap slice:

- item 1: implement S2-02 task-card include gates;
- item 2: implement S2-03 completed-report include gates for explicit new
  reports;
- item 3: implement Step 51 promoted fixture-library gate;
- item 5: integrate I003/I004 seed artifact packages from the parallel agent.

Item 4 is intentionally out of scope because the user assigned it to another
conversation.

## Non-Goals

- Do not touch or stage other-session UI requirements or LGS planning files.
- Do not bulk-validate legacy task cards or completed-task archives.
- Do not promote I003/I004 to practiced status from a single seed example.
- Do not change solver runtime, IO schema, or viewer behavior.
- Do not add Step 51 to the default quality gate.

## Context To Read

- `.codex/skills/task-scoped-session-closer/SKILL.md`
- `.codex/skills/gcs-quality-steward/SKILL.md`
- `.codex/skills/gcs-scene-generation-engineer/SKILL.md`
- `.codex/skills/gcs-ui-design-steward/SKILL.md`
- `docs/agentic/quality-gate-opt-in-policy.md`
- `docs/architecture/68-forward-execution-plan-2026-05-24.md`
- `docs/agentic/agile-pdca-roadmap.md`

## Acceptance Gates

- `run-quality-gates` supports explicit task-card and completed-report
  pathspec includes.
- Unmatched include pathspecs fail.
- Default quality gates still do not scan historical Agentic artifacts.
- A focused Step 51 fixture-library gate validates promoted milestone and
  counterexample scenes against manifest expected CLI outcomes.
- I003/I004 have prompt/template/eval/example seed packages while retaining
  seed status.
- Roadmaps and completed-task archive record the new state and next tasks.

## Verification Plan

```bat
python -m unittest tests.tools.test_agentic_toolkit
python -m unittest tests.tools.test_fixture_library_gate
python tools\scene_generation\fixture_library_gate.py --gcs-exe out\build\clang-ninja\GCS.exe
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-agentic-se-roadmap-items-1-2-3-5.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-25-agentic-se-roadmap-items-1-2-3-5\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-25-agentic-se-roadmap-items-1-2-3-5\README.md --min-score 30
python tools\agentic_design\agentic_toolkit.py run-quality-gates --skip-build --skip-ctest --skip-cli --include-fixture-library --include-task-cards docs\agentic\tasks\2026-05-25-agentic-se-roadmap-items-1-2-3-5.md --include-completed-reports docs\completed-tasks\2026-05-25-agentic-se-roadmap-items-1-2-3-5
python tools\agentic_design\agentic_toolkit.py validate-docs
```

## Evidence Bundle

- `python -m unittest tests.tools.test_agentic_toolkit`: passed, 12 tests.
- `python -m unittest tests.tools.test_fixture_library_gate`: passed, 3 tests.
- `python tools\scene_generation\fixture_library_gate.py --gcs-exe out\build\clang-ninja\GCS.exe`: passed for 3 promoted scenes.
- Remaining closure evidence is recorded in the completed-task archive.

## Residual Risks

- S2-04 legacy archive migration or exemption policy remains pending.
- Closure scoring is still not part of completed-report include gates.
- I003/I004 need future live rendered visual review before any practiced-role
  promotion.
- Other-session item 4 files remain untracked and deliberately unstaged here.
