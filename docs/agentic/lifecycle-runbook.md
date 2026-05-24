# Agentic Lifecycle Runbook

## Goal

Move GCS work from request to push through a repeatable, reviewable agentic
workflow.

Use `task-to-archive-checklist.md` as the compact per-task checklist. The
runbook explains the full workflow; the checklist is the quick gate before
declaring a task done.

## Step 0: Choose Workspace

Choose the workspace before any mutating command.

- Use the local checkout only for read-only work, foreground review,
  integration, or a single active writing session.
- Use a dedicated Codex app Worktree, git worktree, or clone for every parallel
  session that can edit files, generate artifacts, run mutating scripts, or
  switch branches.
- Treat branch state as a repository/worktree fact, not a chat-session fact.
  Do not run `git switch`, `git checkout -b`, or branch cleanup in a shared
  local checkout while another session may be using it.
- Prefer the Codex app Worktree flow. If a manual in-repo worktree is required,
  use `.codex/worktrees/<date>-<slug>`; `.codex/worktrees/` is ignored while
  `.codex/skills/` remains tracked.
- Use stacked branches only when a task truly depends on another unmerged
  branch. Record the parent branch and merge order in the task card.

For non-trivial writing tasks, generate the branch/worktree plan and task card
together:

```bat
python tools\agentic_design\agentic_toolkit.py new-worktree-task --slug my-task --scope tool --risk medium --owner gcs-architecture-steward --base origin/master --request "Describe the task" --write
```

The command prints the git commands to run; it does not create the worktree by
itself. Review the base branch and dirty-tree state before executing them.

## Step 1: Classify

Classify the request by scope:

- `architecture`
- `implementation`
- `test`
- `fixture`
- `ci`
- `docs`
- `tool`
- `review`
- `maintenance`

Classify risk:

- `low`: documentation index, typo, narrow template, focused fixture metadata.
- `medium`: support tooling, quality gates, tests, non-semantic refactors.
- `high`: solver contracts, report codes, numeric behavior, IO migrations,
  runtime commit semantics, third-party dependencies, protected CI behavior.

High-risk tasks require a human gate and an execution plan.

## Step 2: Create A Task Card

Use `new-task-card` or copy `task-card-template.md`, then replace the skeleton
text with task-specific scope, evidence, and residual-risk details.

```bat
python tools\agentic_design\agentic_toolkit.py new-task-card --slug my-task --scope tool --risk medium --owner gcs-contract-tools-steward --request "Describe the task" --write
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\<task>.md
```

For tiny low-risk tasks, the task card may stay in the chat or PR description.
Persist it when the work spans modules, commits, or future follow-up.

When the task will use an isolated worktree, prefer `new-worktree-task` over
`new-task-card` so the worktree path, branch name, base ref, and cleanup command
are recorded at intake time.

## Step 3: Plan

For high-risk tasks, write or attach an execution plan:

- base context;
- ownership;
- refused boundaries;
- steps;
- verification;
- rollback.

Use parallel agents only for independent sidecar work. The architecture steward
keeps final acceptance authority.

## Step 4: Implement

Follow the owning skill. Preserve unrelated user changes. Keep solver runtime
code free of agentic infrastructure.

## Step 5: Verify

Use focused checks first, then the quality gate that fits the scope.

```bat
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-inventory
python tools\agentic_design\agentic_toolkit.py validate-skills
python tools\agentic_design\agentic_toolkit.py check-dependencies
```

For implementation and CI work, run:

```bat
python tools\agentic_design\agentic_toolkit.py run-quality-gates
```

## Step 6: Review

Review for:

- scope control;
- dependency direction;
- public contract evidence;
- missing negative cases;
- skipped checks;
- whether an experience record is needed.

## Step 7: Commit And Push

Stage only scoped files. Commit with a concise message. Push the current
branch. Do not include unrelated dirty files.

## Step 8: Close And Archive

For non-trivial tasks, create or update a completed-task execution report
before declaring the task closed.

```bat
python tools\agentic_design\agentic_toolkit.py new-completed-task-report --slug my-task --session-goal "Describe the completed task" --experience-link docs/agentic/experience/001-task-scoped-session-closure/
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\<task>\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\<task>\README.md --min-score 30
```

Use the score as a closure heuristic, not as a replacement for review. A low
score means the report likely fails to transfer task state into project memory.

Before final response or commit, check the task against
`docs/agentic/task-to-archive-checklist.md`. At minimum, confirm that the task
card, evidence bundle, completed-task archive, roadmap update, and commit scope
agree.

## Step 9: Learn

Create an experience record when:

- the same omission appears twice;
- a high-severity issue escapes review;
- CI fails for a preventable workflow reason;
- a skill, template, fixture, or tool would have prevented the failure.
