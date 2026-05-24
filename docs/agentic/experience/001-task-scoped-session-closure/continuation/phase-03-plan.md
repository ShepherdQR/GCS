# Phase 3 Plan: Empirical Pilot

## Phase Goal

Test the E001 phase-step continuation protocol against real project artifacts.
Phase 3 should find out whether the protocol improves retrieval, review,
resumption, and learning, or whether it adds too much process weight.

## Phase Thesis

The protocol should be judged by future usability:

```text
Can a later agent or reviewer recover intent, evidence, state, and next action
faster because the phase-step protocol was used?
```

## Entry Criteria

Phase 3 may start when:

- Phase 2 examples are complete;
- tooling specification exists;
- validation boundary exists;
- Phase 2 summary replans the pilot;
- `current-status.md` points to Phase 3 Step 3.1.

## Steps

| Step | Artifact | Status | Purpose |
| --- | --- | --- | --- |
| 3.1 | `continuation/phase-03-pilot-selection.md` | planned | Select completed-task reports or active research steps for evaluation. |
| 3.2 | `continuation/phase-03-pilot-results.md` | planned | Apply closure and phase-step rubrics to selected cases. |
| 3.3 | `continuation/phase-03-friction-analysis.md` | planned | Analyze overhead, failure modes, and simplifications. |
| 3.4 | `continuation/phase-03-summary.md` | planned | Close Phase 3 and replan promotion work. |

## Step 3.1: Pilot Selection

Objective:

```text
Choose a small, useful pilot set without turning the pilot into a large audit.
```

Selection criteria:

- at least one completed-task report created before E001 tooling;
- at least one completed-task report created with E001 tooling;
- optionally one active continuation step;
- avoid tasks with unrelated confidentiality or massive artifact size.

## Step 3.2: Pilot Results

Objective:

```text
Apply the E001 closure rubric and phase-step lens to the pilot set.
```

Expected outputs:

- objective reconstruction quality;
- evidence reconstruction quality;
- missing-context questions;
- closure score;
- phase-step fit;
- notable failure modes.

## Step 3.3: Friction Analysis

Objective:

```text
Identify where the protocol helps and where it becomes process drag.
```

Questions:

- Which sections are genuinely useful on resume?
- Which sections feel repetitive?
- Does commit-per-step help or create overhead?
- What should be optional for small research steps?
- What should be mandatory for long or high-risk work?

## Step 3.4: Phase Summary

Objective:

```text
Convert pilot findings into promotion decisions for Phase 4.
```

The summary should decide whether to:

- update the staged E001 skill;
- add eval cases;
- update lifecycle docs;
- implement toolkit commands;
- keep the protocol as E001-only research practice.

## Exit Criteria

Phase 3 is complete when:

- pilot selection exists;
- pilot results exist;
- friction analysis exists;
- Phase 3 summary exists;
- Phase 4 is replanned from evidence, not aspiration;
- `current-status.md` points to Phase 4 Step 4.1.

## Risks

- The pilot set may be too small to generalize.
- The pilot may overfit to docs-heavy tasks.
- The protocol may look good in hindsight but fail during active work.
- Scoring may become performative if not tied to actual resumption quality.

## Current Status

```text
Phase 3 planned, waiting for Phase 2 completion.
```
