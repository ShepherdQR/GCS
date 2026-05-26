---
name: git-session-branch-steward
description: Candidate GCS skill for checking branch, worktree, dirty-state, push, and cleanup safety before mutating Git session state.
---

# Git Session Branch Steward

Status: candidate skill, not active.

Use this skill when work touches Git branch/session ownership, worktrees,
pushes, PR branches, detached HEAD states, or cleanup of Codex worktrees.

## Workflow

1. Run read-only Git inspection first:

   ```bat
   git status --short --branch
   git worktree list
   git branch -vv
   git log --oneline @{u}..HEAD
   ```

2. Classify the current checkout:

   - root integration checkout;
   - task worktree;
   - detached worktree;
   - stale or unknown worktree.

3. Decide push safety:

   - push `codex/<task>` branches by default;
   - do not push `master` when unrelated ahead commits exist;
   - create a clean branch from `origin/master` and cherry-pick scoped commits
     when needed.

4. Preserve unrelated work:

   - stage only current-task files;
   - do not delete, reset, or clean files owned by another session;
   - record detached or unknown worktrees as follow-up.

5. Close with evidence:

   - branch pushed or explicit reason not pushed;
   - task card or completed-task archive updated;
   - cleanup action recorded.

## Promotion Blocker

Do not promote this candidate to active `.codex/skills` until the project has:

- `docs/agentic/git-session-registry.md`, or equivalent durable registry;
- a read-only `check-git-session` command;
- at least one validation record showing the command prevents a bad push or
  stale worktree closure.
