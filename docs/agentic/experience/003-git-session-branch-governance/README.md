---
experience_id: E003-git-session-branch-governance
source: project-practice
status: candidate-agent-and-skill
root_cause: permission_gap
affected_modules:
  - agentic_lifecycle
  - git_workflow
promotion_target: candidate-skill-and-agent
---

# E003: Git Session Branch Governance

## Symptom

Multiple Codex sessions can share a Git checkout while believing they own
separate conversation state. In practice, branch checkout, index state,
worktree dirtiness, and push payload are shared filesystem/Git facts. During
this sequence of work, direct pushes to `master` were unsafe more than once
because local `master` carried unrelated ahead commits; safe branches had to be
created from `origin/master` and populated with scoped commits.

The same session also exposed an unmanaged detached worktree:

```text
C:\Users\QR\.codex\worktrees\d8aa\GCS
```

That worktree had a detached HEAD and untracked nightly-run artifacts. This is
exactly the kind of state that should be visible before an agent edits or
pushes.

## Evidence

- Research report:
  `docs/research/20260524/ai-agent-git-worktree-workflow-for-gcs.md`
- Worktree protocol branch:
  `codex/2026-05-24-git-worktree-protocol`
- Git session branch plan branch:
  `codex/2026-05-26-git-session-branch-governance-plan`
- Session summary branch:
  `codex/2026-05-26-git-session-branch-session-summary`
- Completed task:
  `docs/completed-tasks/2026-05-26-git-session-branch-session-summary/README.md`

## Root Cause

The project had good lifecycle closure practices, but Git session ownership was
still implicit. A chat session can remember intent, but it cannot make a shared
checkout private. Without a registry or preflight check, an agent must infer:

- which branch owns the current work;
- whether the root checkout is an integration workspace or a feature session;
- whether local ahead commits belong to the current request;
- whether an existing detached worktree is abandoned, active, or waiting for
  cleanup.

## Lesson

Git session ownership must be explicit before mutation. Every agentic task that
can edit files or push must know its worktree, branch, base ref, upstream,
dirty state, and cleanup rule before it starts.

The safest default is:

```text
root checkout  -> integration and foreground review
codex worktree -> scoped mutating task
codex branch   -> reviewable change container
registry entry -> durable ownership and cleanup memory
```

## Proposed Promotion

Promotion should be staged:

- T0 experience note: complete in this E003 folder.
- T1 checklist/template update: already partially covered by the worktree
  protocol and session branch plan.
- T2 skill update: candidate `git-session-branch-steward` is included here, but
  should not become active until tool support exists.
- T2 agent role: candidate `git-session-steward` is included here and can be
  used for manual reviews immediately.
- T5 tool gate: implement read-only `check-git-session` and
  `git-session-registry.md`.

## Skill Or Agent Decision

Yes, this pattern deserves extraction, but not as an active skill yet.

Recommended path:

1. Use the candidate agent now for branch/worktree reviews.
2. Implement `git-session-registry.md` and `check-git-session`.
3. Promote the candidate skill to active `.codex/skills` after the command
   exists, so the skill can point to executable evidence rather than prose-only
   caution.

Why not active skill immediately:

- The lesson is clear, but enforcement is still manual.
- A skill without the `check-git-session` tool would mostly repeat rules that
  are already in the runbook.
- The next durable improvement is tooling, not more reminders.

## Validation

Before:

- branch/worktree ownership had to be inferred from ad hoc `git status` and
  memory of prior turns;
- direct push attempts had to be stopped after detecting unrelated ahead
  commits.

After:

- the project has a research report, worktree protocol, session branch plan,
  and this E003 experience record;
- candidate skill and agent material exist for review;
- future implementation has a concrete target: session registry plus
  `check-git-session`.

New gate or eval:

- `check-git-session` should become the focused gate before mutating Git
  commands or pushes.
