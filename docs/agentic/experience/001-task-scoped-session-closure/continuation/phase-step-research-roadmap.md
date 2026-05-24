# E001 Continuation Research Roadmap

## Purpose

Continue researching E001, task-scoped session closure, using a stricter
phase-step operating mode:

```text
plan future work by phase
  -> split each phase into steps
  -> complete one step
  -> summarize the step
  -> update remaining steps in the current phase
  -> commit the completed step
  -> start the next step
  -> after each phase, replan later phases and their steps
```

The research subject is no longer only "how should a session close?" It now
includes a deeper question:

```text
How can long agentic research proceed through accountable micro-closures
without losing adaptability?
```

## Operating Protocol

Every step in this continuation research must produce:

- one concrete artifact or artifact update;
- a short step summary;
- an update to the current phase's remaining steps;
- a scoped commit that excludes unrelated worktree changes;
- a next-step declaration.

Every phase completion must produce:

- a phase summary;
- a reassessment of downstream phases;
- updated phase and step definitions;
- a decision on whether the experience should promote into skill, tool, eval,
  or lifecycle policy.

## Commit Boundary

The current worktree may contain unrelated staged or unstaged changes. For this
continuation research, commits must include only E001 continuation artifacts
unless the user explicitly expands scope.

Preferred commit style:

```text
research: add E001 continuation roadmap
research: define E001 phase-step state machine
research: add E001 step closure template
```

## Phase Plan

| Phase | Goal | Status |
| --- | --- | --- |
| Phase 1 | Define the phase-step research operating model for E001 | in progress |
| Phase 2 | Convert the model into reusable templates and lightweight tooling ideas | planned |
| Phase 3 | Run an empirical pilot over completed-task reports | planned |
| Phase 4 | Promote validated lessons into skill, eval, or lifecycle policy | planned |

## Phase 1: Research Operating Model

Goal: define how E001 continuation research should be conducted as a sequence
of accountable micro-closures.

| Step | Artifact | Status |
| --- | --- | --- |
| 1.1 | `continuation/phase-step-research-roadmap.md` | completed |
| 1.2 | `continuation/phase-step-state-machine.md` | completed |
| 1.3 | `continuation/step-closure-record-template.md` | next |
| 1.4 | `continuation/phase-01-summary.md` | planned |

### Step 1.1 Summary

This step created the durable roadmap for continuing E001 research. It defines
the requested phase-step mode, names the commit boundary, and establishes the
initial phase plan.

### Step 1.1 Update To Remaining Phase 1 Steps

The next step should formalize the state machine behind the protocol before
creating templates. That ordering matters because templates should encode the
state transitions rather than invent them casually.

Updated Phase 1 sequence:

1. Define the state machine and transition rules.
2. Create the step closure record template.
3. Summarize Phase 1 and replan later phases.

### Step 1.2 Summary

This step created `continuation/phase-step-state-machine.md`. It formalizes
step states, phase states, transition rules, scoped commit discipline, phase
completion rules, and failure modes for long-running agentic research.

### Step 1.2 Update To Remaining Phase 1 Steps

The next step should create a step closure record template that encodes the
state machine directly. The template must include branch check, artifact
summary, phase-step update, scoped commit evidence, and next-step declaration.

Updated Phase 1 sequence:

1. Create the step closure record template.
2. Summarize Phase 1 and replan later phases.

## Phase 2: Templates And Tooling Ideas

Initial steps, to be replanned after Phase 1:

1. Define reusable templates for phase plans, step records, and phase
   summaries.
2. Specify possible `agentic_toolkit.py` commands for phase-step research.
3. Decide which checks are deterministic and which require reviewer judgment.

## Phase 3: Empirical Pilot

Initial steps, to be replanned after Phase 2:

1. Select a small set of completed-task reports.
2. Apply E001 closure scoring and the new phase-step lens.
3. Record what the protocol improves and where it creates friction.

## Phase 4: Promotion

Initial steps, to be replanned after Phase 3:

1. Decide whether the phase-step protocol should update an active skill.
2. Add eval cases for missed step summaries, stale plans, and uncommitted
   micro-closures.
3. Update lifecycle docs if the protocol proves generally useful.

## Next Step Declaration

Start Phase 1 Step 1.2:

```text
Create continuation/phase-step-state-machine.md.
```

The state-machine note should define step states, phase states, transition
rules, commit rules, and failure modes for long-running agentic research.
