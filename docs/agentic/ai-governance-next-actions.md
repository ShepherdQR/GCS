# GCS AI Governance Next Actions

Status: active roadmap.
Date: 2026-05-25.

## Purpose

This document keeps the next AI governance work visible after the initial PR
audit and nightly immune-diagnostics design. It is intentionally practical:
each item should either become a tool, a validator, a run artifact, or a
reviewable task card.

## Current Baseline

GCS already has:

- task cards and completed-task archives;
- lifecycle and worktree runbooks;
- opt-in artifact gates;
- module steward skills;
- PR audit governance;
- nightly immune-diagnostics design and automation;
- scene exploration and fixture-promotion boundaries.

The next step is to make these policies executable and measurable.

## Priority 1: Machine-Readable PR Audit

Goal: turn PR audit from a Markdown checklist into a reusable artifact.

Planned outputs:

- `docs/agentic/schemas/pr-audit.schema.json`;
- `python tools\agentic_design\agentic_toolkit.py audit-pr`;
- optional PR description block generated from the JSON;
- later validator once two opt-in cycles are reviewed.

Minimum artifact fields:

- PR class and risk tier;
- affected paths and contracts;
- task-card and completed-archive links;
- evidence passed, failed, and skipped;
- review focus;
- forbidden-action checks;
- findings and next action.

Acceptance signal:

- a reviewer can inspect one JSON file and understand why the PR is or is not
  ready for human review.

## Priority 2: Nightly Diagnostics Calibration

Goal: make night runs comparable before granting them repair authority.

Planned outputs:

- `docs/agentic/nightly-runs/README.md`;
- dated run folders under `docs/agentic/nightly-runs/YYYY-MM-DD/`;
- finding counts by severity and category;
- first-two-run calibration notes;
- repeated-failure detection after three runs.

Calibration labels:

- true finding;
- noise;
- environment setup;
- needs task card;
- safe low-risk patch candidate;
- human gate required.

Acceptance signal:

- after two runs, humans can see whether the nightly agent is producing useful
  signals or mostly environment noise.

## Priority 3: Permission Policy As Code

Goal: make unattended action boundaries explicit enough to validate.

Planned outputs:

- `docs/agentic/agent-permission-policy.md`;
- a lightweight permission-policy validator;
- command/action classes for write, network, dependency, Git, fixture, and
  protected-branch operations.

Forbidden unattended actions:

- merge;
- approve;
- force-push;
- branch deletion;
- fixture promotion;
- dependency installation;
- network-dependent repair;
- solver/runtime/IO/viewer semantic mutation.

Acceptance signal:

- an automation run can state which action class it used and whether a human
  gate was required.

## Priority 4: AI Review Quality Eval Set

Goal: measure whether automated review is helpful instead of merely verbose.

Planned outputs:

- a small historical PR/task eval set;
- human-labeled expected findings;
- `audit-pr` precision and recall notes;
- false-positive and false-negative taxonomy.

Acceptance signal:

- GCS can tune review prompts and validators using project-specific evidence.

## Priority 5: Role Separation For Agents

Goal: prevent the same agentic role from authoring, auditing, repairing, and
approving the same change.

Suggested roles:

- Author Agent: implements the requested change.
- Audit Agent: classifies and reviews; does not repair.
- Repair Agent: handles confirmed findings.
- Nightly Agent: detects and classifies; does not approve.
- Release Gate Agent: prepares merge checklist; does not replace human review.

Acceptance signal:

- a non-trivial PR names which role produced each artifact.

## Priority 6: Governance Metrics

Goal: create trend data before building any dashboard.

Metrics to collect:

- nightly finding count by severity and category;
- repeated skipped checks;
- high-risk PRs without task cards;
- audit findings per PR class;
- repair suggestion acceptance rate;
- repeated-defect close time;
- agent-authored PR rework count.

Acceptance signal:

- a monthly governance summary can be generated from checked-in JSON and
  Markdown artifacts without reading raw chat history.

## Execution Order

1. Implement `pr-audit.schema.json` and `audit-pr`.
2. Implement `nightly-runs/README.md` generation.
3. Run both on the current governance branch as a calibration sample.
4. Add permission-policy-as-code after the first sample output is reviewed.
5. Build the AI review eval set from historical completed-task archives.
