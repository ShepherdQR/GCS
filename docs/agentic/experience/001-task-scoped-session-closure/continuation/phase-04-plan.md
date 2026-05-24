# Phase 4 Plan: Promotion

## Phase Goal

Promote validated E001 continuation lessons into durable project operating
assets. Phase 4 should decide what belongs in skills, evals, lifecycle policy,
or tooling, and what should remain as local research guidance.

## Phase Thesis

Promotion should be evidence-driven:

```text
pilot evidence -> promotion decision -> durable artifact -> validation path
```

Not every useful idea should become a rule. Rules should be promoted only when
they reduce repeated failure, improve resumption, or protect review quality
without imposing excessive ceremony.

## Entry Criteria

Phase 4 may start when:

- Phase 3 pilot results exist;
- friction analysis exists;
- Phase 3 summary names promotion candidates;
- `current-status.md` points to Phase 4 Step 4.1.

## Steps

| Step | Artifact | Status | Purpose |
| --- | --- | --- | --- |
| 4.1 | `continuation/phase-04-skill-promotion-plan.md` | planned | Decide whether the staged E001 candidate skill should be updated or activated. |
| 4.2 | `continuation/phase-04-eval-cases.md` | planned | Define evals for stale plans, missing summaries, and index contamination. |
| 4.3 | `continuation/phase-04-lifecycle-policy.md` | planned | Decide whether the phase-step protocol belongs in general lifecycle docs. |
| 4.4 | `continuation/phase-04-summary.md` | planned | Close the continuation research loop. |

## Step 4.1: Skill Promotion Plan

Objective:

```text
Decide whether phase-step continuation should update the staged
task-scoped-session-closer skill or become an active project skill.
```

Decision options:

- keep as E001-only research guidance;
- update the staged candidate skill under E001;
- promote into `.codex/skills`;
- add as a section to an existing GCS steward skill.

Decision evidence should come from Phase 3.

## Step 4.2: Eval Cases

Objective:

```text
Define reusable eval cases that catch phase-step closure failures.
```

Candidate evals:

- stale plan followed after evidence changed;
- step completed without summary;
- phase completed without replanning downstream phases;
- commit includes unrelated files;
- next step is missing or ambiguous;
- report has strong structure but weak semantic evidence.

## Step 4.3: Lifecycle Policy

Objective:

```text
Decide whether the phase-step protocol should become general GCS lifecycle
policy or remain specialized for long research tasks.
```

Policy questions:

- Which task sizes require phase-step mode?
- Should commit-per-step be mandatory, recommended, or optional?
- Should the lifecycle runbook mention this protocol?
- Should `new-task-card` support planned phases?
- Should completed-task reports include phase summaries?

## Step 4.4: Phase Summary

Objective:

```text
Close E001 continuation research and record final promotion decisions.
```

The summary should name:

- what was promoted;
- what was rejected;
- what remains experimental;
- what future trigger would reopen the experience.

## Exit Criteria

Phase 4 is complete when:

- promotion plan exists;
- eval cases exist;
- lifecycle policy decision exists;
- final summary exists;
- `current-status.md` marks the continuation research complete or deferred
  with a clear reopen trigger.

## Risks

- Promoting too early could make the workflow heavy.
- Promoting too narrowly could bury a useful general practice.
- Eval cases may test formatting instead of real closure quality.
- Lifecycle policy could conflict with lightweight task flow if thresholds are
  not clear.

## Current Status

```text
Phase 4 planned, waiting for Phase 3 evidence.
```
