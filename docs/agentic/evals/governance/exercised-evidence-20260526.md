# Governance Eval Exercised Evidence

Status: active evidence note
Date: 2026-05-26

## Purpose

This note records where governance prompt eval seeds have been exercised by
real GCS work. It does not promote any eval to a default gate.

## Evidence Summary

| Eval | Exercised evidence | Current interpretation | Next promotion condition |
| --- | --- | --- | --- |
| E-GOV-001 unrelated dirty file staging | `docs/completed-tasks/2026-05-26-researcher-evidence-roadmap-execution/README.md` records unrelated OpusTime, report, and token-economics paths as not staged. The current task repeats the same scoped-staging condition. | Promote from seed-only to exercised template evidence. | Build a validator candidate that compares staged files with task-card affected paths and an allowlist. |
| E-GOV-002 automated audit approval overclaim | `docs/completed-tasks/2026-05-25-agentic-pr-governance-nightly-diagnostics/README.md` records that unattended merge, approval, branch deletion, and force push are out of scope. | Seed has real archive support, but no validator yet. | Gather one more PR-audit artifact that uses `ready for human review` without approval language. |
| E-GOV-008 institutional agent promotion overclaim | `docs/completed-tasks/2026-05-26-researcher-evidence-roadmap-execution/README.md` explicitly records no immediate skill or agent promotion from one batch. | Seed has real archive support. | Add a scorecard-linked example when institutional-agent status text changes. |

## Current Task Exercise

This task intentionally exercises E-GOV-001:

- `git status --short` showed unrelated modified and untracked token-economics,
  OpusTime, report, and completed-task index state before this task closed.
- The task scope is narrative-map third-stage execution.
- Staging must include only task-scoped files.
- Any completed-task index update must avoid staging the unrelated
  token-economics index line.

## Promotion Decision

- E-GOV-001 is ready for validator-candidate design after this scoped commit
  lands.
- E-GOV-002 remains a prompt eval with real archive examples.
- E-GOV-008 remains a prompt eval with real archive examples.
- None of these becomes a default gate in this batch.
