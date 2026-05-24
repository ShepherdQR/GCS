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
| Phase 1 | Define the phase-step research operating model for E001 | complete |
| Phase 2 | Build reusable phase-step examples, anti-examples, and tool specifications | next |
| Phase 3 | Run an empirical pilot over completed-task reports | planned |
| Phase 4 | Promote validated lessons into skill, eval, or lifecycle policy | planned |

## Phase 1: Research Operating Model

Goal: define how E001 continuation research should be conducted as a sequence
of accountable micro-closures.

| Step | Artifact | Status |
| --- | --- | --- |
| 1.1 | `continuation/phase-step-research-roadmap.md` | completed |
| 1.2 | `continuation/phase-step-state-machine.md` | completed |
| 1.3 | `continuation/step-closure-record-template.md` | completed |
| 1.4 | `continuation/phase-01-summary.md` | completed |

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

### Step 1.3 Summary

This step created `continuation/step-closure-record-template.md`. The template
encodes the state machine into a reusable record format with objective,
artifact, state transition, phase update, commit boundary, evidence, residual
risk, and next-step declaration sections.

### Step 1.3 Update To Remaining Phase 1 Steps

Only the Phase 1 summary remains. It should evaluate whether the roadmap, state
machine, and template are enough to open Phase 2, then replan the Phase 2
steps using what Phase 1 learned.

Updated Phase 1 sequence:

1. Summarize Phase 1 and replan later phases.

### Step 1.4 Summary

This step created `continuation/phase-01-summary.md`. It closes Phase 1,
summarizes what the phase established, and replans Phases 2-4 with more
specific artifact targets.

### Phase 1 Completion Update

Phase 1 is complete. Phase 2 should begin with examples before tooling, because
validators and commands need concrete positive and negative shapes to encode.

## Phase 2: Examples And Tooling Specifications

Replanned after Phase 1:

1. Create `continuation/phase-02-example-records.md` with strong and weak step
   closure examples.
2. Create `continuation/phase-02-tooling-spec.md` with candidate toolkit
   commands.
3. Create `continuation/phase-02-validation-boundary.md` to separate
   deterministic checks from reviewer judgment.
4. Create `continuation/phase-02-summary.md` and replan the empirical pilot.

## Phase 3: Empirical Pilot

Replanned after Phase 1, to be refined after Phase 2:

1. Select pilot reports or active research steps.
2. Apply closure and phase-step rubrics.
3. Analyze friction, overhead, and simplifications.
4. Summarize Phase 3 and replan promotion.

## Phase 4: Promotion

Replanned after Phase 1, to be refined after Phase 3:

1. Decide whether the phase-step protocol should update an active skill.
2. Add eval cases for missed summaries, stale plans, and index contamination.
3. Decide whether lifecycle docs should adopt the protocol.
4. Close the continuation research loop.

## Next Step Declaration

Start Phase 2 Step 2.1:

```text
Create continuation/phase-02-example-records.md.
```

The next artifact should provide one strong and one weak example of a step
closure record so Phase 2 tooling can be grounded in concrete cases.
