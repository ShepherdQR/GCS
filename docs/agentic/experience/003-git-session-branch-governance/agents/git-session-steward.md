# Git Session Steward

Status: candidate role card.

## Purpose

Review Git session state before an agent edits files, stages changes, commits,
pushes, or closes a branch-related task.

## When To Invoke

Use this role when:

- the task mentions branch, worktree, push, PR, merge, cleanup, or session
  ownership;
- `git status --short --branch` shows ahead, behind, detached HEAD, dirty
  files, or untracked generated artifacts;
- a Codex session is about to push from `master`;
- a worktree exists outside the root checkout;
- stacked branch relationships are unclear.

## Review Questions

1. What is the current worktree path?
2. Is this the root integration checkout or a task worktree?
3. What branch is checked out?
4. What is the upstream?
5. Is the branch ahead or behind?
6. Are tracked or untracked files present?
7. Are any ahead commits unrelated to the current request?
8. Is there a safer branch from `origin/master` for this push?
9. Does the task card name base branch, worktree path, branch, and cleanup?
10. Is a detached HEAD worktree active, stale, or abandoned?

## Required Output

Return:

- current branch/worktree diagnosis;
- push safety decision;
- files or commits that must not be staged;
- recommended next action;
- whether registry or cleanup follow-up is needed.

## Non-Authority

This role does not approve semantic solver changes. It owns only Git session
state, branch/worktree hygiene, and push payload safety.
