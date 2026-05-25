# Long-Running Agent Operations

Date: 2026-05-25

## Question

What makes a long-running or standing agent task safe enough to run repeatedly?

## Pattern

A long-running task is safe only when it has a bounded objective, isolated
workspace, explicit cadence, clear stop conditions, recoverable failures,
budget controls, and durable output artifacts.

## Aspects

### Cadence

Nightly tasks should run when the repository is least likely to be under active
foreground editing. For GCS, `02:30 Asia/Shanghai` is a good default because it
separates the run from normal daytime development and leaves morning review
time.

### Workspace

Use a dedicated worktree. OpenAI Codex documents worktrees for automations so
background changes do not interfere with local work. GCS already has a
worktree policy in `docs/agentic/lifecycle-runbook.md`; the nightly workflow
should reuse it.

### Budget

The run should limit itself:

- maximum one report directory per scheduled run;
- maximum one optional repair branch/diff;
- no repeated full builds after the first failure unless a later stage depends
  on them;
- stop after classifying failures and writing a useful summary.

### Failure Recovery

Jules documents automatic retries for transient failures and marks repeated
failure as failed. GCS should follow a conservative variant:

- retry transient environment/setup once;
- do not retry destructive or mutating commands;
- if setup fails twice, classify as `environment_setup` and stop;
- always write a failure summary with exact command and remediation suggestion.

### Human Escalation

The automation should ask for human input or produce a task card candidate
when:

- a high-risk solver contract change is suggested;
- a dependency/network change is needed;
- fixture promotion is suggested;
- a branch or history operation would be destructive;
- repeated nightly failures indicate project-level drift.

## Nightly Task Lifecycle

```text
start run
  -> create dated run directory
  -> inspect repo status and current branch
  -> run lightweight agentic docs gates
  -> run focused scene-explorer inventory checks
  -> run selected quality gates with skips recorded
  -> classify defects
  -> propose repairs
  -> optionally prepare isolated repair diff
  -> write summary
  -> stop
```

## Output Contract

Each run directory should contain:

- `README.md`: human summary;
- `findings.json`: machine-readable finding list;
- `commands.md`: command evidence and interpreted results;
- `repair-plan.md`: suggested fixes and whether they are safe for automation;
- optional `patch.diff`: only when a repair diff was produced;
- optional `task-card-candidate.md`: for work that should become a formal task.

## GCS Decision

Nightly diagnostics should be a triage and evidence engine, not an unattended
maintainer with merge authority.
