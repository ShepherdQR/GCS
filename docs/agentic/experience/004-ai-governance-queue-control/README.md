---
experience_id: E004-ai-governance-queue-control
source: project-practice
status: candidate-experience
root_cause: queue_drift_risk
affected_modules:
  - agentic_lifecycle
  - ai_governance
  - repository_audit
promotion_target: candidate-skill-or-tool-after-reuse
---

# E004: AI Governance Queue Control

## Symptom

AI governance work can produce many valuable next actions at once: PR audit
gates, nightly diagnostics, permission policy, repository audit, Git session
ownership, evals, metrics, and product-facing narrative. Without a persisted
queue, the next session must reconstruct priority from raw chat and recent
commits.

## Evidence

This session had multiple valid governance threads in flight:

- PR audit policy and `validate-pr-audit`;
- nightly immune-diagnostics design;
- repository-audit reporting, diff, trend, gate, and snapshot registry work;
- Git session branch governance and candidate steward material;
- narrative/product/metrics follow-up from AI organization research.

The durable response is
`docs/agentic/ai-governance-execution-plan-2026-05-26.md`.

## Root Cause

The project has strong task cards and archives, but a cross-cutting governance
queue can still become implicit. Completed-task archives say what finished.
Roadmaps say broad direction. The missing object is a compact operational queue
that translates "what remains" into ordered, reviewable tasks with acceptance
signals.

## Lesson

When a session asks "what remains?" and then authorizes execution, the answer
should be promoted from chat into a dated execution plan before the next
implementation step starts.

The plan should name:

- order;
- status;
- output;
- acceptance signal;
- promotion or skill decision;
- review triggers.

## Skill Or Agent Decision

Do not promote an active skill yet.

Candidate future skill:

- name: `ai-governance-queue-steward`;
- trigger: user asks for remaining AI governance/audit work, long-running
  governance plan, or queue reprioritization;
- responsibilities: inspect current governance artifacts, produce ordered
  queue, update task docs, and refuse active-skill promotion without reuse
  evidence.

Promotion threshold:

- at least two successful queue reuse cycles, or
- one concrete failure where a missing persisted queue caused duplicated,
  unordered, or unsafe governance work.

Current status:

- candidate experience only;
- no active `.codex/skills` change;
- next executable work belongs in validators and registry tooling.

## New Gate Or Eval Idea

A future eval should present an agent with several completed governance tasks
and ask it to answer "what next?" The expected response must persist an ordered
queue and refuse to promote a new skill prematurely.
