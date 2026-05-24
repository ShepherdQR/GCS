# Agentic Lifecycle Runbook

## Goal

Move GCS work from request to push through a repeatable, reviewable agentic
workflow.

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

## Step 9: Learn

Create an experience record when:

- the same omission appears twice;
- a high-severity issue escapes review;
- CI fails for a preventable workflow reason;
- a skill, template, fixture, or tool would have prevented the failure.
