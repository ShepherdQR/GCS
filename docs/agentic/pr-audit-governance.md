# GCS PR Audit Governance

Status: proposed v1.
Date: 2026-05-25.

## Purpose

This document makes pull requests first-class governance objects in the GCS
agentic software-engineering workflow. It complements the lifecycle runbook,
task cards, evidence bundles, quality gates, and completed-task archives.

The goal is not to make every small change ceremonial. The goal is to make
agent-authored, agent-reviewed, and exploratory PRs reviewable without raw chat
context.

## Governance Thesis

Agents may research, edit, test, comment, and propose fixes. They may not
self-approve, self-merge, hide skipped evidence, or bypass module ownership.

Every non-trivial PR should answer:

- What class of change is this?
- Which GCS contract or process boundary owns it?
- What evidence proves it is ready for human review?
- What should reviewers inspect first?
- What is intentionally out of scope?
- What residual risk remains?

## PR Classes

| Class | Use when | Required evidence |
| --- | --- | --- |
| `architecture` | Durable docs define module boundaries, contracts, lifecycle policy, or quality-gate policy | `validate-docs`; architecture steward review; task card for non-trivial changes |
| `solver-contract` | C++ public contracts, report codes, state versions, diagnostics, IO, runtime, viewer bridge | focused tests; build/CTest or explicit skip risk; owning module steward |
| `quality-gate` | Tests, fixtures, CI gates, golden reports, validation tools | focused tests; gate docs; negative cases when behavior changes |
| `agentic-process` | Task cards, archives, skills, automations, institutional agents, lifecycle runbooks | task-card/completed-report gates when applicable; closure evidence |
| `scene-exploration` | Scene generation, scratch exploration, promotion packages, fixture dry runs | deterministic IDs/seeds; validation reports; no fixture promotion without explicit gate |
| `exploratory` | Research branch, trial implementation, spike, or discovery output | draft status; explicit non-merge default; findings summary; promotion path |
| `repair` | Fix for a known audit, CI, nightly, review, or user-reported finding | finding link; minimal diff; revalidation |
| `docs-only` | Low-risk documentation, index, or wording update | docs validation or explicit low-risk skip |

## Risk Tiers

| Tier | Criteria | Required posture |
| --- | --- | --- |
| Low | Docs-only, index update, wording, non-semantic report cleanup | May stay commit-note-only if lifecycle runbook allows |
| Medium | Agentic process docs, support tooling, quality-gate docs, deterministic report schema | Task card; focused validation; archive if future tasks depend on it |
| High | Solver/runtime/IO/viewer semantics, report codes, fixture promotion, dependency policy, default CI behavior, protected branch behavior | Task card before edits; human gate reason; focused and broad evidence; completed archive |

## Required PR Audit Fields

A PR audit should produce this summary:

```yaml
pr_class: architecture | solver-contract | quality-gate | agentic-process | scene-exploration | exploratory | repair | docs-only
risk_tier: low | medium | high
decision: ready_for_human_review | needs_author_revision | needs_human_gate | exploratory_only | blocked
task_card: path-or-none
completed_archive: path-or-none
affected_contracts:
  - contract-or-process-name
affected_paths:
  - path
evidence:
  passed:
    - command summary
  failed:
    - command summary
  skipped:
    - check: name
      reason: reason
      risk: risk
review_focus:
  - subject
forbidden_action_check:
  merge: not_performed
  approve: not_performed
  force_push: not_performed
  branch_delete: not_performed
  fixture_promotion: not_performed_or_explicit
findings:
  - severity: P0 | P1 | P2 | P3
    category: boundary | evidence | correctness | security | maintainability | docs | process
    subject: path-or-contract
    summary: finding
next_action: human_review | revise | create_task_card | run_gate | split_pr | close_exploratory
```

The machine-readable v1 form is defined at
`docs/agentic/schemas/pr-audit.schema.json`.

## Toolkit Prototype

Use the first executable audit pass as an advisory reviewer aid:

```bat
python tools\agentic_design\agentic_toolkit.py audit-pr --base origin/master --head HEAD
```

The command:

- reads changed paths from Git;
- infers PR class, risk tier, affected contracts, and review focus;
- records recommended evidence as skipped unless the caller supplies
  `--evidence-passed`, `--evidence-failed`, or `--evidence-skipped`;
- marks forbidden unattended actions as `not_performed`;
- emits JSON matching `gcs.pr-audit.v1`.

It does not run tests, approve PRs, merge, push, delete branches, promote
fixtures, or replace human review.

## Review Rubric

### Intent Fit

- Does the diff match the user request, task card, and non-goals?
- Did the agent avoid opportunistic cleanup?
- Is exploratory work clearly labeled as exploratory?

### Boundary Fit

- Does solver truth stay in solver contracts?
- Does viewer code stay read-only over snapshots and reports?
- Do IO adapters avoid mutating solver internals?
- Does agentic process stay out of runtime solver dependencies?
- Are scene generator policies kept in `tools/scene_generation`?

### Evidence Fit

- Are checks appropriate to the risk tier?
- Are skipped checks explained as risk?
- Are negative cases present when contracts or gates changed?
- Are generated artifacts deterministic and provenance-backed?

### Review Fit

- Does the PR tell reviewers what to inspect first?
- Are high-risk paths and contracts named?
- Are AI-generated comments focused on P0/P1 risks?
- Are lower-priority issues summarized rather than flooding the review?

## Exploratory PR Policy

Exploratory PRs are allowed and useful. They must remain safe.

Rules:

- default to draft;
- include `exploratory` in the PR class;
- state the learning goal and stop condition;
- do not promise merge readiness;
- do not promote fixtures or change default gates;
- end with one of: close, convert to task card, split into repair PR, or
  promote a documented architecture decision.

Exploratory PRs should be reviewed for insight quality, not only code quality.
Their most valuable output may be a report, taxonomy, failure reproduction, or
design constraint.

## Automated Review Boundaries

Automated PR audit may:

- classify the PR;
- detect missing evidence;
- flag module-boundary drift;
- recommend reviewers;
- propose focused fixes;
- ask for additional tests;
- summarize skipped checks.

Automated PR audit must not:

- approve the PR;
- merge the PR;
- mark high-risk work as ready without human gate evidence;
- force-push or delete branches;
- silently broaden the scope;
- count itself as a required human approval.

## GCS Review Checklist

Before merging a non-trivial PR, confirm:

- task card exists or lifecycle low-risk rule explains why not;
- PR class and risk tier are clear;
- affected contracts are named;
- review focus names the first files/contracts to inspect;
- focused evidence ran;
- broad evidence ran or skipped checks are recorded;
- generated artifacts have provenance;
- no forbidden actions occurred;
- completed archive exists or is planned for closure;
- roadmap update is included when project direction changed.

## Suggested PR Description Template

```markdown
## Summary

- Class:
- Risk:
- Task card:
- Completed archive:

## Intent And Scope

<What this PR changes and what it intentionally does not change.>

## Review Order

1. <path or contract>
2. <path or contract>

## Evidence

- Passed:
- Failed:
- Skipped:

## Contract Impact

- Affected contracts:
- Report codes:
- Fixtures/generated artifacts:

## Residual Risk

- <risk or none>

## Automated Audit

- Decision:
- Findings:
```

## Promotion Path

This document should become a gate only after two clean opt-in cycles:

1. Use it manually on this PR and the next non-trivial PR.
2. Record findings in completed-task archives.
3. Decide whether to add a machine-readable PR audit artifact.
4. Only then consider an opt-in validator.
