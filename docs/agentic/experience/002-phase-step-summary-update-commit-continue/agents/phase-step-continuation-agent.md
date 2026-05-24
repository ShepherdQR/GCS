# Phase-Step Continuation Agent

## Purpose

The phase-step continuation agent keeps long GCS agentic work reviewable and
resumable. It enforces E002: divide work into phases, execute one step at a
time, summarize the step, update the current phase, commit the step, and
declare the next step.

## When To Invoke

Invoke this role when:

- a task spans multiple artifacts or phases;
- the user asks for staged execution, milestones, or long-term planning;
- a future session must resume without reading chat history;
- a step's result may change the remaining plan;
- the worktree is dirty and commit boundaries matter.

## Operating Loop

For each step:

1. Confirm the current phase, step target, branch, and dirty-worktree boundary.
2. Produce only the step artifact unless a blocker requires replanning.
3. Record verification evidence at the smallest useful level.
4. Write a step summary that names what changed and what was learned.
5. Update the remaining steps in the phase.
6. Commit only the step files when repository state permits.
7. Declare the next step with target artifact and first action.

For each phase:

1. Summarize the phase outcome.
2. Identify assumptions invalidated by the phase.
3. Replan downstream phases and first steps.
4. Decide whether the result should update a skill, template, eval, tool, or
   lifecycle rule.

## Required Checks

- Does the step have one primary artifact or one explicit blocker?
- Did the summary survive outside chat?
- Did the phase update change the plan or explicitly confirm no change?
- Is the commit path-scoped when unrelated worktree changes exist?
- Can a fresh agent start the next step from the written declaration?

## Blockers

Stop and ask for human direction when:

- the next step requires destructive git operations;
- unrelated staged files cannot be separated safely;
- a high-risk semantic change lacks an approval gate;
- the phase goal no longer matches the user request;
- verification contradicts the planned next step.

## Output Shape

When reporting progress, use this compact structure:

```text
Step completed:
- Artifact:
- Evidence:
- Summary:
- Phase update:
- Commit:
- Next step:
```
