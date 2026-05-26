# Agentic Task Closure Demo

Status: seed
Date: 2026-05-26

## Claim

GCS can run a non-trivial AI-assisted project task as an inspectable
organization: it scopes the task, writes durable artifacts, validates the
changed surface, archives the result, and pushes only the intended files.

This is a product demo because it shows how a user can trust the project
process, not just the solver output.

## Demo Flow

| Step | What the user sees | Evidence artifact |
| --- | --- | --- |
| 1. Request | A broad user intent is reduced to a scoped work package. | `docs/architecture/95-gcs-narrative-map.md` |
| 2. Task card | The agent records scope, non-goals, evidence, and residual risk. | `docs/agentic/tasks/2026-05-26-next-stage-mainline-evidence.md` |
| 3. Durable outputs | The task produces architecture, product, and governance docs. | `docs/architecture/96-fixture-corpus-maturity-ladder.md`, `docs/product/gcs-demo-ladder.md`, `docs/agentic/permission-threat-matrix.md` |
| 4. Validation | The agent runs task, archive, docs, inventory, skill, and dependency gates. | Completed-task evidence block |
| 5. Archive | The completed work is summarized without raw chat logs. | `docs/completed-tasks/2026-05-26-next-stage-mainline-evidence/README.md` |
| 6. Scoped commit | The push excludes unrelated dirty work. | Git status and commit-scope review |

## What This Demonstrates

- The repository can explain what changed, why it changed, and what was not
  touched.
- Documentation-only work still has evidence gates.
- Agentic governance is connected to product value through demo and onboarding
  artifacts.
- Future sessions can resume from files instead of chat history.

## Acceptance Criteria

A reviewer should be able to answer these questions in one sitting:

- What was the user intent?
- What files were produced?
- What checks ran?
- What checks were skipped and why?
- What remains as future work?
- Which unrelated files were intentionally excluded?

## Current Evidence

The strongest current closure example is:

- `docs/completed-tasks/2026-05-26-next-stage-mainline-evidence/README.md`

The current batch extends the same demo pattern with:

- `docs/agentic/agentic-organization-operating-map.md`
- `docs/agentic/institutional-agent-registry-and-scorecard.md`
- `docs/agentic/governance-eval-roadmap.md`
- `docs/completed-tasks/2026-05-26-ai-organization-narrative-execution/README.md`

## Known Limits

- This seed demo is documentation-based. It does not yet include a screen
  recording, command transcript artifact, or rendered walkthrough.
- It demonstrates process trust, not solver numerical behavior.
- It depends on the completed-task archive being kept indexed and current.

## Next Upgrade

Turn this seed into a full D0 demo package by adding:

1. a short command transcript showing validator output;
2. a before/after file list;
3. a compact diagram of request to archive flow;
4. a product-facing README section that points new contributors to this demo
   before the deeper architecture docs.
