# GCS Agentic Organization Operating Map

Status: active
Date: 2026-05-26

## Thesis

The GCS agentic organization is not a parallel story beside the solver. It is
the operating system that turns human intent into solver evidence, product
evidence, and reviewable project memory.

The core promise is simple:

- no non-trivial work without an owner and boundary;
- no claim of completion without evidence;
- no durable rule without reuse or eval pressure;
- no agentic process artifact that cannot be traced back to solver, product, or
  governance value.

## Operating Layers

| Layer | Purpose | Durable outputs | Primary owner |
| --- | --- | --- | --- |
| Intent and portfolio | Translate user intent into a scoped project move. | Narrative map, roadmap notes, task cards. | `gcs-architecture-steward` |
| Workspace boundary | Keep parallel work, dirty files, and branch scope legible. | Worktree plans, branch notes, git status evidence. | `task-scoped-session-closer` |
| Context and memory | Recover the relevant project state without replaying chat logs. | Research reports, completed-task archives, timelines. | `002-tailor-stitch-timeline` |
| Execution roles | Route work to domain-specific steward skills. | Skill-guided edits, module-specific docs, focused checks. | Module and process stewards |
| Evidence gates | Prove the changed surface with the smallest meaningful checks. | Validation logs, closure scores, skipped-check rationale. | `gcs-quality-steward` |
| Governance and permissions | Bound what agents may do without human approval. | Permission policy, threat matrix, PR audit records. | Governance docs and reviewers |
| Review and archive | Turn finished work into reusable memory. | Completed-task reports, indexes, evidence bundles. | `task-scoped-session-closer` |
| Learning and promotion | Convert repeated pressure into templates, evals, and institutional roles. | Experience records, evals, prompts, templates, skills. | Institutional agents |

## Lifecycle

```text
request
  -> classify scope and risk
  -> create task card for non-trivial work
  -> read architecture, product, and agentic context
  -> edit, implement, or research inside the chosen boundary
  -> run focused evidence gates
  -> update indexes, metrics, and plans
  -> archive completed work
  -> stage only scoped files
  -> commit and push
  -> promote lessons only after evidence
```

The lifecycle is intentionally conservative. It protects the repository from
over-claiming while still allowing a single agent session to move from
research to implementation to push.

## Role Topology

| Role family | What it decides | What it must not own |
| --- | --- | --- |
| Architecture stewards | Module boundaries, target vocabulary, narrative map, public contracts. | Runtime truth without code and tests. |
| Quality stewards | Gate selection, validation posture, regression evidence, skipped-check risk. | Product positioning or aesthetic preference. |
| Product and demo stewards | User workflows, demo ladder, onboarding, inspectable value. | Solver semantics or module dependency direction. |
| Institutional agents | Recurring project memory, timeline, visual review, reusable lessons. | Promotion of one-off practices into rules without evidence. |
| Session closers | Archive, evidence bundle, commit boundary, scoped handoff. | Rewriting the technical substance after the task is done. |

## Evidence Contract

Every non-trivial task should leave four kinds of evidence:

| Evidence kind | Question answered | Typical artifact |
| --- | --- | --- |
| Scope evidence | What was intentionally changed and excluded? | Task card and archive. |
| Behavior evidence | Did the relevant surface still work? | Tests, validators, generated reports, screenshots. |
| Governance evidence | Was the agent allowed to take each action? | Permission notes, skipped-check rationale, PR audit. |
| Memory evidence | Can a later session resume without chat logs? | Completed-task report, index, timeline, experience note. |

For docs-only work, behavior evidence is usually the agentic validator suite and
explicitly skipped build or UI checks. For solver or viewer work, behavior
evidence must include focused code, fixture, CLI, CTest, visual, or replay
checks.

## Relationship To Solver Evidence

The agentic organization should be measured by how reliably it produces solver
evidence:

- task cards prevent ambiguous solver changes;
- module stewards keep local edits aligned with target contracts;
- fixture and demo ladders connect internal correctness to user-visible value;
- PR audit and permission policy prevent unreviewed mutation of protected
  surfaces;
- completed-task archives preserve how evidence was generated.

If an agentic artifact cannot improve solver evidence, product evidence,
governance, or learning, it should remain a note rather than becoming an active
process rule.

## Operating Cadence

| Cadence | Activity | Update target |
| --- | --- | --- |
| Every non-trivial task | Task card, validation, archive, scoped commit. | `docs/agentic/tasks/`, `docs/completed-tasks/` |
| After narrative or governance work | Metrics and narrative map refresh. | `docs/agentic/metrics-dashboard.md`, `docs/architecture/95-gcs-narrative-map.md` |
| After repeated friction | Experience capture or eval candidate. | `docs/agentic/experience/`, `docs/agentic/evals/` |
| Before role promotion | Scorecard review and refusal eval evidence. | `docs/agentic/institutional-agent-registry-and-scorecard.md` |
| Before public release | Demo ladder, onboarding, and release readiness review. | `docs/product/` |

## Anti-Patterns

- A process doc that cannot name the protected boundary it improves.
- A completed archive that says "done" without validation or skipped-check
  risk.
- A role marked institutional only because it has a clever name.
- A demo that displays architecture but does not let a user inspect evidence.
- An automated audit that implies approval, merge permission, or human review.

## Next Moves

1. Keep this map as the compact entry point for agentic organization design.
2. Use the registry scorecard before promoting new institutional agents.
3. Convert governance eval candidates into executable checks only after two or
   more examples or a severe near miss.
4. Connect every future product demo back to task, solver, or governance
   evidence.
