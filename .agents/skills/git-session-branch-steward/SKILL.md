---
name: git-session-branch-steward
description: Git session and branch governance for GCS. Invoke when work touches git branches, worktrees, push safety, PR branches, detached HEAD states, session ownership, or cleanup of stale worktrees. Ensures scoped staging, safe push payloads, and preservation of unrelated dirty files.
---

# Git Session Branch Steward

## Mission

Prevent the most common agentic governance failure mode: pushing unrelated dirty
files, staging files owned by another session, or operating on the wrong branch.
This skill owns git session state, branch/worktree hygiene, and push payload
safety.

## Trigger Conditions

Invoke when:
- The task mentions branch, worktree, push, PR, merge, cleanup, or session
  ownership
- `git status --short --branch` shows ahead, behind, detached HEAD, dirty files,
  or untracked generated artifacts
- An agent is about to push from `master` with unrelated ahead commits
- A worktree exists outside the root checkout
- Stacked branch relationships are unclear
- Session closure requires branch cleanup decisions

## Pre-Mutation Checklist

Before any `git commit`, `git push`, `git branch -D`, or `git reset`:

1. **Inspect current state**:
   ```bash
   git status --short --branch
   git worktree list
   git branch -vv
   git log --oneline @{u}..HEAD
   ```

2. **Classify the checkout**:
   - Root integration checkout — never push from here unless explicitly authorized
   - Task worktree — safe to push its branch
   - Detached or stale worktree — record, do not delete without authorization

3. **Check push safety**:
   - Push task branches by default
   - Do not push `master` when unrelated ahead commits exist
   - When `master` has ahead commits, create a clean branch from `origin/master`
     and cherry-pick scoped commits

4. **Preserve unrelated work**:
   - Stage only current-task files
   - Do not delete, reset, or clean files owned by another session
   - Record detached or unknown worktrees as follow-up

5. **Close with evidence**:
   - Branch pushed or explicit reason not pushed
   - Task card or archive updated
   - Cleanup action recorded

## Guardrails

- Never skip hooks (`--no-verify`, `--no-gpg-sign`) unless the user explicitly
  asks for it
- Never push `master` directly when unrelated ahead commits exist — create a
  task branch and cherry-pick
- Never delete a worktree without confirming it is stale and has no unmerged
  work
- Stage only scoped files; never use `git add -A` or `git add .`
- Before any destructive operation (`git reset --hard`, `git checkout --`,
  `git branch -D`), confirm with the user

## Required Output

Return:
- Current branch/worktree diagnosis
- Push safety decision with rationale
- Files or commits that must not be staged
- Recommended next action
- Whether registry or cleanup follow-up is needed

## Codex Integration

When invoked:
- Use `Bash` with `git status --short --branch` and `git worktree list` for
  initial diagnosis
- Use `Bash` with `git log --oneline @{u}..HEAD` to check ahead commits
- Use `Bash` with `git diff --stat` to verify staged scope before commit
- Use `Read` on `.Codex/current-task` to cross-check task scope against staged
  files
- Record push decisions and cleanup actions in the task archive
- Flag any unrelated dirty files in the session handoff
