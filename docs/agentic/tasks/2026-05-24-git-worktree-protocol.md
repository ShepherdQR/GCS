---
task_id: 2026-05-24-git-worktree-protocol
status: complete
request: "Implement the GCS multi-session Codex git worktree protocol and push it."
scope: tool
risk: medium
owning_agent: gcs-architecture-steward
specialist_agents:
  - none
affected_contracts:
  - none
affected_paths:
  - .gitignore
  - docs/agentic/
  - docs/completed-tasks/
  - docs/research/20260524/ai-agent-git-worktree-workflow-for-gcs.md
  - tools/agentic_design/agentic_toolkit.py
required_evidence:
  - ast-parse-agentic-toolkit
  - new-worktree-task-smoke
  - validate-task-card
  - validate-completed-task-report
  - validate-docs
human_gate_required: false
human_gate_reason: ""
---

# 2026-05-24-git-worktree-protocol

## Scope

Implement the practical GCS workflow for multi-session Codex work:

- make `.codex/worktrees/` an ignored local worktree root;
- document the workspace boundary in the agentic runbook, README, and closure
  checklist;
- add `new-worktree-task` to the agentic toolkit so future tasks can generate
  a branch/worktree plan and task card together;
- archive this process change as a completed task.

Workspace rationale: this task intentionally used the current Local checkout
because the user asked to implement and push the project policy from the active
thread, and no separate parallel writer was required for this scoped workflow
change.

## Non-Goals

- Do not create a real git worktree during this task.
- Do not switch branches while implementing this task.
- Do not modify solver, scene, IO, runtime, or viewer semantics.
- Do not stage unrelated `.codex_scene_generation_store/` files.

## Context To Read

- `docs/research/20260524/ai-agent-git-worktree-workflow-for-gcs.md`
- `docs/agentic/lifecycle-runbook.md`
- `docs/agentic/task-to-archive-checklist.md`
- Owning skill: `gcs-architecture-steward`

## Acceptance Gates

- The runbook names Local, Worktree, and clone boundaries before classification.
- The checklist has an explicit Workspace gate.
- The toolkit command emits deterministic branch, worktree path, task-card path,
  and git commands without mutating Git state.
- Ignore rules preserve tracked `.codex/skills/` while excluding local
  `.codex/worktrees/`.
- The commit scope excludes unrelated untracked scene-generation store files.

## Verification Plan

```bat
python -c "import ast, pathlib; ast.parse(pathlib.Path('tools/agentic_design/agentic_toolkit.py').read_text(encoding='utf-8'))"
python tools\agentic_design\agentic_toolkit.py new-worktree-task --slug git-worktree-protocol-smoke --request "Smoke test worktree task planning" --scope tool --risk low --owner gcs-architecture-steward --base origin/master --json
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-git-worktree-protocol.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-24-git-worktree-protocol\README.md
python tools\agentic_design\agentic_toolkit.py validate-docs
```

## Evidence Bundle

Initial checks already run:

```text
python tools\agentic_design\agentic_toolkit.py new-worktree-task --help
Passed: command is registered and argparse help renders.

python tools\agentic_design\agentic_toolkit.py new-worktree-task --slug git-worktree-protocol-smoke --request "Smoke test worktree task planning" --scope tool --risk low --owner gcs-architecture-steward --base origin/master --json
Passed: emitted task_id, branch, task card, worktree path, and commands without creating a worktree.
```

Final validation evidence is recorded in the completed-task archive for this
task.

Final checks:

```text
python -c "import ast, pathlib; ast.parse(pathlib.Path('tools/agentic_design/agentic_toolkit.py').read_text(encoding='utf-8'))"
Passed: toolkit parses without writing bytecode.

python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-git-worktree-protocol.md
Passed: task card validation.

python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-24-git-worktree-protocol\README.md
Passed: completed-task archive validation.

python tools\agentic_design\agentic_toolkit.py validate-docs
Passed: module design coverage.

python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-24-git-worktree-protocol\README.md --min-score 30
Passed: closure score 38/40.

git diff --check
Passed: no whitespace errors; Git emitted line-ending conversion warnings only.
```

## Residual Risks

This task installs the protocol and planning command, but it does not enforce
worktree use at Codex app session creation time. Human/operator discipline is
still required until Codex app worktree selection or a project wrapper becomes
the normal entry point.
