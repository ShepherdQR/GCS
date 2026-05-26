# 20-Minute Contributor Path

Status: active
Date: 2026-05-26

## Purpose

This path helps a technically strong reviewer understand GCS in one sitting.
It is not a full onboarding manual. It is the minimum route from a fresh local
checkout to the project's thesis, evidence model, and safe contribution
workflow.

## Before You Start

Use PowerShell from the repository root:

```bat
cd C:\Codes\Trae\s002_GCS\GCS
```

Check for local work before running mutating commands:

```bat
git status -sb
```

If there are unrelated dirty files, do not stage or overwrite them. GCS often
has parallel agent sessions in progress.

## Minute 0-3: Read The Thesis

Read:

- `README.md`
- `docs/architecture/95-gcs-narrative-map.md`
- `docs/product/gcs-product-user-brief.md`

You should be able to say:

```text
GCS solves geometric constraints by producing evidence-rich local-to-global
reports, and it builds itself through an evidence-rich agentic organization.
```

## Minute 3-6: Learn The Architecture Vocabulary

Read:

- `docs/architecture/README.md`
- `docs/architecture/10-system/current-to-target-map.md`

Key module names:

- `kernel`
- `constraint_catalog`
- `incidence_graph`
- `decomposition_planner`
- `diagnostics`
- `numeric_engine`
- `session_runtime`
- `io_adapters`
- `viewer_bridge`

Rule of thumb:

- durable solver truth belongs in architecture and contracts;
- process truth belongs in `docs/agentic`;
- product/user truth belongs in `docs/product`;
- viewer state must not become hidden solver truth.

## Minute 6-9: Inspect The Evidence Assets

Read:

- `docs/architecture/96-fixture-corpus-maturity-ladder.md`
- `fixtures/scene/milestone/README.md`
- `fixtures/scene/counterexamples/README.md`
- `docs/product/gcs-demo-ladder.md`

You should understand why a failing scene can still be a valuable asset.

## Minute 9-12: Run Lightweight Repo Validators

Run:

```bat
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-inventory
python tools\agentic_design\agentic_toolkit.py validate-skills
python tools\agentic_design\agentic_toolkit.py check-dependencies
```

Expected result:

- all four checks pass on a healthy docs and architecture batch.

If a command fails because of local permission or environment issues, record
the failure as environment evidence. Do not treat skipped checks as passes.

## Minute 12-15: Learn The Agentic Workflow

Read:

- `docs/agentic/lifecycle-runbook.md`
- `docs/agentic/task-to-archive-checklist.md`
- `docs/agentic/metrics-dashboard.md`
- `docs/agentic/permission-threat-matrix.md`

You should understand:

- when a task needs a task card;
- why non-trivial work closes with an archive;
- which actions require human gates;
- why unrelated dirty files must be preserved.

## Minute 15-18: Find A First Safe Contribution

Good first contribution types:

- clarify a doc link or index;
- add evidence to an existing task archive;
- classify one saved fixture under the corpus ladder;
- add a D1 or D2 demo note without changing solver behavior;
- add a negative eval for a documented workflow failure.

Avoid as a first contribution:

- solver semantics;
- IO schema migrations;
- dependency changes;
- fixture promotion;
- branch cleanup;
- UI state ownership changes.

## Minute 18-20: Close The Loop

For any non-trivial change:

```bat
python tools\agentic_design\agentic_toolkit.py new-task-card --slug <slug> --scope docs --risk medium --owner gcs-architecture-steward --request "<request>" --write
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\<task>.md
```

Before commit:

```bat
git diff --cached --name-status
```

Make sure the staged files are only the task-owned files.

## Done When

After 20 minutes, a reviewer should know:

- the GCS thesis;
- the target module vocabulary;
- where fixtures and counterexamples live;
- how demos should prove solver evidence;
- how task cards, archives, metrics, and permission gates keep agentic work
  reviewable;
- what not to touch without a task card and human gate.

## Next Onboarding Upgrade

The next version should add a tested command transcript for:

- one D1 smoke demo;
- one D2 diagnostic classification demo;
- one D3 replay evidence demo;
- one viewer workbench screenshot path.
