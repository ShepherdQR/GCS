# Phase 2 Plan: Examples And Tooling Specifications

## Phase Goal

Build concrete examples, anti-examples, and tooling specifications for the
phase-step continuation protocol. Phase 1 defined the operating model. Phase 2
must make that model easier to evaluate and eventually automate.

## Phase Thesis

Tools should not be designed from abstract ideals alone. They need concrete
positive and negative cases:

```text
examples -> validation boundaries -> tooling specification
```

Phase 2 therefore begins with examples before CLI design.

## Entry Criteria

Phase 2 may start when:

- Phase 1 is complete;
- `phase-step-state-machine.md` exists;
- `step-closure-record-template.md` exists;
- `phase-01-summary.md` has replanned Phase 2;
- `current-status.md` says Phase 2 Step 2.1 is ready.

## Steps

| Step | Artifact | Status | Purpose |
| --- | --- | --- | --- |
| 2.1 | `continuation/phase-02-example-records.md` | ready | Provide strong and weak examples of step closure records. |
| 2.2 | `continuation/phase-02-tooling-spec.md` | planned | Specify candidate `agentic_toolkit.py` commands for phase-step continuation. |
| 2.3 | `continuation/phase-02-validation-boundary.md` | planned | Separate deterministic checks from reviewer judgment. |
| 2.4 | `continuation/phase-02-summary.md` | planned | Summarize Phase 2 and replan Phase 3. |

## Step 2.1: Example Records

Objective:

```text
Show what a high-quality and low-quality step closure record look like.
```

Required content:

- one strong example;
- one weak example;
- commentary explaining why the strong example works;
- commentary explaining why the weak example fails;
- mapping back to the state machine and template.

Step completion rule:

- update this phase plan;
- update `current-status.md`;
- commit only Step 2.1 files.

## Step 2.2: Tooling Specification

Objective:

```text
Specify possible commands that could help agents run phase-step continuation.
```

Candidate commands:

- `new-phase-plan`;
- `validate-phase-plan`;
- `new-step-closure-record`;
- `validate-step-closure-record`;
- `phase-status`;
- `next-step`.

This step should not implement tools yet. It should define command intent,
inputs, outputs, validation limits, and failure modes.

## Step 2.3: Validation Boundary

Objective:

```text
Decide which parts of phase-step continuation are machine-checkable and which
require reviewer judgment.
```

Expected categories:

- deterministic structure checks;
- repository-state checks;
- heuristic scoring;
- human or agent semantic judgment;
- checks that should not exist because they would create ceremony.

## Step 2.4: Phase Summary

Objective:

```text
Close Phase 2 and replan the empirical pilot in Phase 3.
```

The summary should decide whether tooling design is mature enough for a pilot
or whether more examples are needed.

## Exit Criteria

Phase 2 is complete when:

- example records exist;
- tooling specification exists;
- validation boundary exists;
- Phase 2 summary exists;
- Phase 3 has been replanned;
- `current-status.md` points to Phase 3 Step 3.1.

## Risks

- The examples may become too polished and fail to represent real mistakes.
- The tooling spec may overreach before the process is empirically tested.
- Validation may reward structure while missing meaning.

## Current Status

```text
Phase 2 Step 2.1 ready.
```
