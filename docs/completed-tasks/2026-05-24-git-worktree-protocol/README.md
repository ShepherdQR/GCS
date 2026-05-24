---
task_id: 2026-05-24-git-worktree-protocol
status: complete
session_goal: "Implement the GCS multi-session Codex git worktree protocol and push it."
archive_target: docs/completed-tasks/2026-05-24-git-worktree-protocol
experience_links:
  - none
---

# Git Worktree Protocol

## Task Objective

Turn the prior research report on multi-session Codex Git isolation into
project practice: document the workspace rules, ignore the local worktree root,
add an agentic toolkit command for worktree task planning, and preserve the
change as a reviewable lifecycle artifact.

## Scope And Non-Goals

In scope:

- `.gitignore` now excludes `.codex/worktrees/` without excluding tracked
  `.codex/skills/`.
- `docs/agentic/lifecycle-runbook.md` now starts with a workspace-choice gate.
- `docs/agentic/README.md` and `task-to-archive-checklist.md` expose the new
  minimum workflow and closure check.
- `tools/agentic_design/agentic_toolkit.py` now includes `new-worktree-task`.

Out of scope:

- No actual worktree was created.
- No branch switching was performed.
- No solver, IO, scene, runtime, viewer, fixture, or CMake behavior changed.
- Unrelated untracked `.codex_scene_generation_store/` files were left alone.

## Interaction Summary

The user asked whether the proposed worktree practices were already
implemented, then asked to implement and push them if missing. The repository
already had a lifecycle runbook and task tooling, but lacked a workspace gate,
ignore rule, and worktree task helper. This task added those pieces.

## Work Completed

- Added a Step 0 workspace boundary to the lifecycle runbook.
- Added `new-worktree-task` to generate a branch/worktree/task-card plan without
  mutating Git state.
- Added `.codex/worktrees/` to ignore rules while preserving `.codex/skills/`.
- Added checklist and README references so the practice is visible during task
  intake and closure.
- Added this task card and archive.

## Files And Artifacts

- `.gitignore`: ignores `.codex/worktrees/`.
- `docs/agentic/lifecycle-runbook.md`: documents Local, Worktree, clone,
  stacked-branch, and task-card intake practices.
- `docs/agentic/README.md`: updates the minimum workflow and file map.
- `docs/agentic/task-to-archive-checklist.md`: adds the Workspace closure gate.
- `tools/agentic_design/agentic_toolkit.py`: adds `new-worktree-task`.
- `docs/agentic/tasks/2026-05-24-git-worktree-protocol.md`: task record.
- `docs/completed-tasks/2026-05-24-git-worktree-protocol/README.md`: archive.

## Evidence

```text
python tools\agentic_design\agentic_toolkit.py new-worktree-task --help
Passed: command is registered and argparse help renders.

python tools\agentic_design\agentic_toolkit.py new-worktree-task --slug git-worktree-protocol-smoke --request "Smoke test worktree task planning" --scope tool --risk low --owner gcs-architecture-steward --base origin/master --json
Passed: emitted deterministic JSON with task_id, branch, base, task_card, worktree_path, and commands.

python -m py_compile tools\agentic_design\agentic_toolkit.py
Skipped as a bytecode check because the sandbox could not create tools\agentic_design\__pycache__; AST parsing was used instead.

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

## Decisions

- `new-worktree-task` prints worktree commands but does not run them. This keeps
  the helper deterministic and avoids hidden mutating Git operations.
- `.codex/worktrees/` is ignored precisely because `.codex/skills/` is tracked
  project configuration.
- The active Local checkout was used for this implementation because this task
  installed the protocol itself and the user requested a direct push from the
  current project state.

## Skipped Checks And Risks

- Full build and CTest are not relevant to this docs/tool workflow change.
- The protocol is documented and tool-assisted, but not yet automatically
  enforced by Codex app session creation.
- Pushing `master` will also publish commits that were already ahead of
  `origin/master` before this task.

## Follow-Up

- Consider a future wrapper that creates the worktree after an explicit
  operator confirmation.
- Consider adding a lightweight lint that warns when `.codex/worktrees/` is not
  ignored.

## Archive Handoff

- Archive path: `docs/completed-tasks/2026-05-24-git-worktree-protocol`
- Related experience:
  - none
- Skill, eval, fixture, or tool update needed: no immediate skill promotion;
  the new toolkit command and runbook gate carry the practice for now.
