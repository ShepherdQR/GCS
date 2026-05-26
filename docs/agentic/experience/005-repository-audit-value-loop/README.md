---
experience_id: E005-repository-audit-value-loop
source: project-practice
status: candidate-experience
root_cause: audit_value_traceability_gap
affected_modules:
  - repository_audit
  - session_efficiency
  - agentic_lifecycle
promotion_target: candidate-skill-after-reuse
---

# E005: Repository Audit Value Loop

## Thesis

Repository audit is most useful when it forms a closed value loop:

```text
accepted snapshot
  -> scoped diff
  -> completed-task audit delta
  -> session-efficiency record
  -> roadmap decision
  -> next accepted snapshot
```

The loop turns repository shape into reviewable engineering memory without
confusing raw lines or file counts with value.

## Problem

The repository-audit work started as a counting question: how many files, how
many lines, how many skills or agents, and where to see the overview. That
quickly exposed a deeper governance problem. A project can collect metrics but
still fail to answer:

- whether a task's repository delta matched the intended scope;
- whether token or time cost produced durable, validated artifacts;
- whether growth belongs to source, tests, fixtures, tools, research, reports,
  or agentic process assets;
- whether trend decisions are based on accepted baselines or dirty scratch
  snapshots.

## Lesson

Use accepted baselines for project-level trend and staged-index diffs for
task-level evidence.

The safe sequence is:

1. Collect accepted snapshots from committed revisions only.
2. Generate registry and accepted-trend reports from manifests.
3. Before commit, stage the task scope and compare `HEAD` to the staged index.
4. Store compact `repository-audit-delta.md` sections in completed-task
   archives.
5. Record session-efficiency separately, marking token telemetry `unknown`
   when exact counts are unavailable.
6. Promote thresholds only after enough comparable samples exist.

## Evidence

This experience is supported by the repository-audit task chain:

- `docs/completed-tasks/2026-05-26-repository-audit-snapshot-registry/README.md`
- `docs/completed-tasks/2026-05-26-repository-audit-plan-execution/README.md`
- `docs/reports/repository-audit/README.md`
- `docs/reports/repository-audit/trend.md`
- `docs/reports/session-efficiency/2026-05-26/README.md`
- `tools/repository_audit/README.md`
- `tools/session_efficiency/README.md`

## Skill Or Agent Decision

Do not promote an active skill yet.

Candidate future skill:

- name: `repository-audit-value-loop-steward`;
- trigger: user asks to close a metrics-heavy task, compare token cost to
  durable output, or update accepted audit baselines;
- responsibilities: ensure accepted snapshot, staged diff, archive delta,
  session-efficiency record, and roadmap decision stay consistent.

Candidate future agent:

- name: `measure-tradeoff`;
- role: review repository-audit delta and session-efficiency records for
  non-blocking governance recommendations;
- promotion threshold: at least two more completed tasks using
  `repository-audit-delta.md` and at least three session-efficiency records.

Current status:

- candidate experience only;
- no active `.codex/skills` change;
- no institutional-agent promotion;
- next evidence should come from repeated task archives, not from more theory.

## Gate Or Eval Idea

A future eval should present:

- one accepted baseline;
- one dirty worktree with unrelated changes;
- one staged task scope;
- one completed-task archive missing audit delta.

The expected behavior is to refuse dirty-worktree trend interpretation, use the
staged index for the task delta, keep token telemetry unknown if unavailable,
and recommend no skill promotion until reuse evidence exists.

## Operating Invariants

- Accepted snapshots measure committed revisions, not arbitrary dirty state.
- `var/` remains scratch; durable reports live under `docs/reports/`.
- Token-efficiency denominators are `n/a` when telemetry is unknown.
- Raw line growth is not a value proxy without validation and closure evidence.
- Skill or agent promotion requires repeated successful reuse or a concrete
  failure that the promotion would have prevented.
