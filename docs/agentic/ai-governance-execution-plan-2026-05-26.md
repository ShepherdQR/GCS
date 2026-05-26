# AI Governance And Audit Execution Plan

Status: active plan
Date: 2026-05-26

## Purpose

This plan persists the current execution order for GCS AI governance and audit
work. It starts from the current repository state after PR audit governance,
nightly immune-diagnostics design, permission policy validation, repository
audit reporting, and Git session cleanup.

The plan is intentionally operational. Each step should produce one of:

- a validator;
- a machine-readable artifact;
- a durable run record;
- a completed-task archive;
- a candidate experience, skill, or agent record.

## Current Baseline

The current governance surface includes:

- task cards and completed-task archives for non-trivial work;
- lifecycle, worktree, branch, and PR governance docs;
- `audit-pr` and `validate-pr-audit`;
- PR audit JSON artifacts and schema;
- nightly immune-diagnostics design and run folder contract;
- permission-as-code policy for unattended agent actions;
- repository-audit collector, reports, diffs, trends, opt-in gate support, and
  the first accepted snapshot registry;
- Git session branch governance experience and candidate steward material.

## Execution Order

| Order | Task | Status | Output | Acceptance |
| --- | --- | --- | --- | --- |
| 0 | Git/worktree cleanup and branch stitching | done | single root worktree on `master` | no leftover local or remote session branches; `master` aligned with `origin/master` before this batch |
| 1 | Persist current task queue and session closeout | current | this plan plus completed-task archive | future agent can resume without reading raw chat |
| 2 | Finish repository-audit snapshot registry closeout | current | accepted snapshot manifest, index, task card, archive | `index` renders accepted snapshots and focused tests pass |
| 3 | Nightly diagnostics calibration | next | first two dated run reviews with labels | findings classified as true, noise, setup, task-card needed, safe patch candidate, or human gate |
| 4 | PR audit opt-in quality gate | next | `run-quality-gates --include-pr-audit` or equivalent scoped flag | selected PR audit JSON validates through the common gate entry point |
| 5 | Git session registry and preflight checker | next | `git-session-registry.md` and `check-git-session` | mutating Git work reports worktree, branch, base, dirty state, and cleanup rule before edits |
| 6 | Permission action log and threat matrix | next | automation action-log schema plus threat matrix | unattended runs classify filesystem, network, branch, dependency, fixture, and communication actions |
| 7 | AI review eval set | next | small historical task/PR eval set | expected findings and false positive/false negative taxonomy exist |
| 8 | PR description generator | later | Markdown PR summary from PR audit JSON | reviewer can create a PR description without reading raw chat |
| 9 | Governance metrics rollup | later | monthly or milestone summary | metrics come from checked-in JSON/Markdown, not chat reconstruction |

## Step Details

### 1. Current Plan And Session Closeout

Scope:

- persist this execution order;
- archive the current session;
- decide whether this session creates new experience or skill material;
- push scoped changes.

Acceptance:

- `docs/agentic/ai-governance-execution-plan-2026-05-26.md` exists;
- `docs/completed-tasks/2026-05-26-ai-governance-plan-session-closeout/README.md`
  records the session summary and next queue;
- the experience decision is explicit and linked from the archive.

### 2. Repository-Audit Snapshot Registry

Scope:

- close the existing registry implementation task;
- keep accepted snapshots separate from local scratch snapshots;
- anchor accepted baselines to committed revisions.

Acceptance:

- `docs/reports/repository-audit/2026-05-26/manifest.json` records the
  accepted baseline;
- `docs/reports/repository-audit/README.md` renders the registry index;
- focused repository-audit tests pass.

### 3. Nightly Diagnostics Calibration

Scope:

- inspect the first two nightly run folders;
- label every finding;
- identify repeated failure patterns and environmental noise;
- keep automated repair authority off until calibration is trustworthy.

Acceptance:

- each finding has one calibration label;
- repeated findings are grouped;
- safe repair candidates are separated from human-gated findings.

### 4. PR Audit Opt-In Gate

Scope:

- integrate `validate-pr-audit` into the shared quality-gate entry point;
- keep validation opt-in rather than broad-scanning historical audits.

Acceptance:

- a selected PR audit file can be validated by `run-quality-gates`;
- missing, invalid, or risky ready-state PR audits fail the selected gate;
- legacy PR audit artifacts are not pulled into default validation.

### 5. Git Session Registry And Preflight Checker

Scope:

- implement read-only session ownership registry;
- add a preflight checker before mutating Git workflows.

Acceptance:

- checker reports current worktree, branch, upstream, base ref, dirty state,
  ahead/behind, and registered owner;
- unsafe direct push conditions are visible before staging or commit.

### 6. Permission Action Log And Threat Matrix

Scope:

- connect permission policy to concrete run logs;
- summarize risk categories for private data, untrusted content, outbound
  communications, dependency/network actions, fixture promotion, branch
  mutation, and protected-branch operations.

Acceptance:

- automation or nightly runs can state action class, gate status, and human
  approval requirement;
- high-risk action classes cannot silently appear as successful unattended
  work.

### 7. AI Review Eval Set

Scope:

- select a small sample from completed-task archives and PR audit artifacts;
- define expected review findings and non-findings;
- record prompt/tool tuning lessons.

Acceptance:

- the eval can reject both verbose but useless reviews and false completion;
- `audit-pr` improvements can be measured against project-specific labels.

## Promotion And Skill Decisions

Promote only when there is evidence, not just a good idea.

Current decisions:

- E001 task-scoped session closure remains the active closeout skill.
- E003 Git session branch governance remains a candidate skill/agent until
  `check-git-session` exists.
- This plan creates a new candidate experience for governance queue control,
  but it should not become an active skill until the queue has at least two
  successful reuse cycles or a missed queue handoff causes a concrete failure.

## Review Cadence

Review this plan when:

- the next nightly calibration cycle completes;
- `run-quality-gates` gains PR audit include support;
- `check-git-session` lands;
- a permission action log schema is introduced;
- a new default governance gate is proposed.
