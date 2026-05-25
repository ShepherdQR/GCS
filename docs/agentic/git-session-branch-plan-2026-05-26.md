# Git Session Branch Governance Plan

Snapshot: 2026-05-26, Asia/Shanghai.

## Current Repository State

Read-only Git check at planning time:

- Root checkout: `C:\Codes\Trae\s002_GCS\GCS`.
- Root branch: `master`.
- Root upstream: `origin/master`.
- Root commit: `98ac47e merge: integrate agentic governance execution`.
- Worktrees: only the root checkout is registered.
- Dirty state: there are existing modified and untracked files from other
  active work, including agentic governance docs, agentic tooling tests,
  permission-policy docs, PR-audit artifacts, and task archives.

Interpretation:

- The root checkout has returned to the integration branch, which is good.
- The root checkout is not clean, so new session-branch work must avoid staging
  unrelated files.
- The previous immediate problem, feature branches occupying the root checkout,
  is not present at this snapshot.
- The next risk is governance drift: sessions can still create branches,
  worktrees, task cards, and generated artifacts without a durable registry or
  preflight check.

## Goal

Make Git session branching explicit, auditable, and low-friction for Codex work
on GCS.

The target operating model:

```text
root checkout       = integration / foreground review
task worktree       = isolated mutating session
branch              = reviewable change container
PR or merge record  = governance decision
task card           = intent, base, evidence, and risk trace
session registry    = active branch/worktree inventory
```

## Principles

1. A chat session does not own a branch; a worktree owns the checked-out branch.
2. Root `master` is not a general-purpose scratchpad.
3. A feature branch in root is allowed only as a short foreground exception.
4. Every mutating parallel session needs an isolated worktree or clone.
5. Every branch needs a base, owner, purpose, status, and cleanup rule.
6. Stacked branches are dependencies, not naming decoration.
7. Default-branch pushes require explicit authorization and scoped staging.
8. Generated artifacts must be either ignored, promoted, or archived before
   closure.

## Remaining Plan

### S3-01 Root Integration Contract

Define the root checkout contract in `docs/agentic/lifecycle-runbook.md`:

- root is for integration, review, and single foreground work only;
- root should normally track `origin/master`;
- if root moves to a feature branch, that fact must be visible in the session
  registry;
- root must be clean before branch switches, merges, or direct pushes.

Acceptance evidence:

- runbook section exists;
- task-to-archive checklist has a root/dirty-state check;
- current status is recorded before closing a task.

### S3-02 Git Session Registry

Create `docs/agentic/git-session-registry.md` as a lightweight table:

```text
session_id
branch
worktree_path
base_ref
upstream
owner
purpose
status
opened_at
last_seen_commit
cleanup_action
```

Recommended statuses:

```text
planned
active
ready_for_review
pushed
merged
abandoned
stale
closed
```

The registry should not be a chat log. It should be a durable inventory of
active and recently closed Git sessions.

### S3-03 `check-git-session`

Add a read-only command to `tools/agentic_design/agentic_toolkit.py`:

```bat
python tools\agentic_design\agentic_toolkit.py check-git-session
```

It should report:

- current branch and upstream;
- current worktree path and whether it is root;
- dirty tracked files;
- untracked files, grouped by known local stores;
- whether `master` is ahead or behind `origin/master`;
- whether the current branch is listed in the session registry;
- whether the current branch is checked out in more than one worktree;
- whether the branch name follows `codex/<date-or-topic>` conventions.

The command must not fetch, switch branches, stage files, or mutate worktrees.

### S3-04 Worktree Creation With Explicit Opt-In

Extend `new-worktree-task` in two layers:

1. Current behavior stays the default: print deterministic commands and write a
   task card when `--write` is passed.
2. Add a separate explicit flag later, for example `--create-worktree`, that
   runs `git worktree add` only after the operator intentionally asks for it.

The command should optionally update the session registry after the worktree is
created.

### S3-05 Branch Lifecycle And Cleanup

Define a lifecycle:

```text
planned -> active -> ready_for_review -> pushed -> merged -> closed
planned -> active -> abandoned -> closed
active -> stale -> revived_or_closed
```

Closure rules:

- merged branches should be deleted locally and remotely;
- clean worktrees should be removed with `git worktree remove`;
- stale worktrees should be inspected before removal;
- task cards or archives should record whether cleanup happened or why it was
  deferred.

### S3-06 Stacked Branch Policy

Use stacked branches only when the child branch depends on unmerged parent
changes.

Each stacked task must record:

```text
parent_branch
child_branch
PR base
merge_order
rebase_policy
blocked_by
```

Branch names may contain slashes, but slashes do not create a Git hierarchy.
The parent relationship must be written in the task card or registry.

### S3-07 Push And PR Policy

Default:

- push `codex/<task>` branches;
- open PRs for review;
- avoid direct `master` pushes unless the user explicitly requests and the
  staged payload is only the intended scope.

Before any push:

```bat
git status --short --branch
git diff --cached --name-only
git log --oneline @{u}..HEAD
```

If the branch has unrelated local commits, push a safer codex branch or stop for
explicit approval.

### S3-08 Generated Artifact Routing

Generated files should have one of three states:

```text
ignored local store
promoted fixture/artifact
completed-task archive evidence
```

Unclassified generated artifacts should block task closure when they appear in
`git status --short`.

### S3-09 Session Handoff Template

Add a compact handoff section to task cards and completed-task reports:

```text
Current branch:
Base branch:
Worktree:
Upstream:
Dirty state:
Pushed branch:
PR:
Cleanup needed:
Next owner:
```

This is the durable answer to "which session owns this branch?"

## Priority Recommendation

Implement next in this order:

1. S3-02 Git Session Registry.
2. S3-03 `check-git-session`.
3. S3-01 Root Integration Contract.
4. S3-05 Branch Lifecycle And Cleanup.
5. S3-04 explicit worktree creation.
6. S3-06 stacked branch policy.
7. S3-07 push/PR policy.
8. S3-08 generated artifact routing.
9. S3-09 session handoff template.

The first two items give the most leverage: they make the current Git state
visible before Codex writes anything.

## Current Snapshot Decision

Do not create a worktree for this planning-only update. The root checkout is on
`master` and aligned with `origin/master`, but it contains unrelated dirty
files. This task should stage only the new persistent planning files and leave
all existing modified or untracked files untouched.
