# Phase-Step State Machine

## Purpose

This note formalizes the phase-step mode for continuing E001 research. The
goal is to make long agentic research adaptable without becoming vague. The
state machine gives each step and phase a visible lifecycle, so planning,
execution, summary, update, and commit become explicit transitions rather than
informal habits.

## Core Model

```text
phase plan
  -> step ready
  -> step in progress
  -> step artifact produced
  -> step summarized
  -> remaining steps updated
  -> scoped commit created
  -> next step declared
```

After the last step in a phase:

```text
phase summarized
  -> downstream phases reassessed
  -> phase plan updated
  -> next phase opened
```

## Step States

| State | Meaning | Required Evidence To Leave State |
| --- | --- | --- |
| `planned` | The step exists in a phase plan but is not ready to execute. | Scope and artifact are named. |
| `ready` | The step can begin without more planning. | Inputs and target path are known. |
| `in_progress` | The agent is actively producing the step artifact. | Work is bounded to the step. |
| `artifact_ready` | The artifact exists but has not been summarized. | File or change exists in the workspace. |
| `summarized` | The step result and rationale are recorded. | Step summary is written. |
| `phase_updated` | Remaining steps in the phase have been revised. | Phase plan reflects what was learned. |
| `committed` | The step has a scoped commit. | Commit hash or commit result exists. |
| `next_declared` | The following step has a clear start point. | Next-step declaration exists. |
| `blocked` | The step cannot proceed safely. | Blocker and needed decision are recorded. |
| `superseded` | The step is no longer the right move. | Replacement step and reason are recorded. |

## Phase States

| State | Meaning |
| --- | --- |
| `planned` | Phase goal and initial steps are known. |
| `open` | At least one step is in progress or ready. |
| `replanning` | A completed step changed the phase shape. |
| `complete` | All required phase steps are done and summarized. |
| `promoted` | Phase output has updated a skill, tool, eval, or lifecycle rule. |
| `deferred` | Phase remains valuable but is intentionally paused. |
| `abandoned` | Phase goal is no longer useful or valid. |

## Transition Rules

### Step Start

A step may move from `ready` to `in_progress` only when:

- the target artifact is named;
- the expected step output is small enough to review;
- unrelated dirty worktree changes are identified or explicitly ignored;
- the current branch is known.

The current branch check matters. A step-level commit should never assume it is
on the same branch as the previous step.

### Artifact Ready

A step may move to `artifact_ready` when the promised artifact exists. For a
documentation step, this usually means a new or updated markdown file. For a
tooling step, it means code exists but may not yet be verified.

### Summary

A step may move to `summarized` when the artifact states:

- what changed;
- why it changed;
- what was learned;
- what remains uncertain.

The summary can live inside the artifact itself, in the phase roadmap, or in a
separate step record. It must be durable.

### Phase Update

A step may move to `phase_updated` only after remaining phase steps are
rechecked. The point is not to obey the old plan blindly. The point is to make
plan change explicit.

Update questions:

- Did this step change the next step?
- Did this step reveal a missing step?
- Did this step make a later step unnecessary?
- Did risk or scope change?

### Commit

A step may move to `committed` only after the commit boundary is checked.

Commit boundary checklist:

- current branch is recorded;
- staged files are inspected;
- unrelated staged files are not included;
- commit command names exact paths when the worktree is dirty;
- commit message identifies the step outcome.

When the index already contains unrelated staged files, use a path-scoped
commit strategy rather than a plain `git commit`.

### Next Declaration

A step may move to `next_declared` when the next step has:

- artifact target;
- short purpose;
- immediate first action.

This declaration prevents the next session from spending its first turn
rediscovering where to resume.

## Phase Completion Rules

A phase may close only when:

- every required step is `committed`, `superseded`, or intentionally deferred;
- phase output is summarized;
- downstream phases are replanned;
- promotion target is considered.

The phase summary must answer:

- what the phase established;
- what it invalidated or changed;
- what later phases should now do differently;
- whether any skill, tool, eval, or lifecycle document should change.

## Failure Modes

### Stale Plan

The agent keeps following a phase plan after evidence changes. Prevention:
require `phase_updated` after every step.

### Uncommitted Micro-Closure

The artifact exists but no step commit is created. Prevention: treat commit as
a step state, not an optional cleanup.

### Branch Drift

The agent assumes it is on the same branch as the previous step. Prevention:
check `git branch --show-current` before each step commit.

### Index Contamination

Unrelated staged files enter a step commit. Prevention: inspect staged files
and use path-scoped commit commands in dirty worktrees.

### Template Theater

The step record has headings but no real summary or update. Prevention: require
each step to change the phase plan or explicitly confirm it remains valid.

### Infinite Replanning

The agent keeps revising plans without producing artifacts. Prevention: every
step must produce one concrete artifact or a recorded blocker.

## Step 1.2 Summary

This step defined the state machine for E001 continuation research. It adds
explicit step states, phase states, transition rules, commit boundary checks,
phase completion rules, and failure modes.

## Update To Remaining Phase 1 Steps

The next step should create a step closure record template. It should encode
the states defined here, including branch check, scoped commit evidence, phase
update, and next-step declaration.

The final Phase 1 summary should then evaluate whether the state machine and
template are enough to begin Phase 2 tooling design.
