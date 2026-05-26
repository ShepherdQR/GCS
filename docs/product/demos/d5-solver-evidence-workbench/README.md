# D5 Solver Evidence Workbench Package

Status: active static package
Date: 2026-05-26
Audience: solver and geometric-constraint researchers

## Claim

GCS can package the intended Solver Evidence Workbench view as a static,
evidence-first screenshot artifact that links geometry, diagnostic classes,
replay timeline, and research boundaries.

This package is a static workbench evidence board. It is not a live GUI claim.

## Inputs

| Input | Role |
| --- | --- |
| `docs/product/demos/d2-diagnostic-classification/artifacts/d2-diagnostic-summary.json` | Diagnostic classification evidence. |
| `docs/product/demos/d3-replay-evidence/artifacts/g1-replay-evidence.report.json` | Replay and transaction evidence. |
| `docs/architecture/92-gcs-ui-architecture-adjustment-record.md` | Workbench direction and UI posture. |
| `docs/architecture/75-ui-design-system-conventions.md` | Evidence-first interface grammar. |

## Generated Artifacts

| Artifact | Meaning |
| --- | --- |
| `docs/product/demos/d5-solver-evidence-workbench/artifacts/d5-workbench-evidence.png` | Static evidence-board screenshot. |
| `docs/product/demos/d5-solver-evidence-workbench/artifacts/screenshot-baselines.json` | Screenshot baseline manifest for the D5 package. |

## Generation Command

```bat
python tools\product_demo\d5_workbench_package.py --output docs\product\demos\d5-solver-evidence-workbench\artifacts\d5-workbench-evidence.png --manifest docs\product\demos\d5-solver-evidence-workbench\artifacts\screenshot-baselines.json
```

## Visual QA Command

```bat
python tools\ui_qa\gcs_screenshot_baseline.py --manifest docs\product\demos\d5-solver-evidence-workbench\artifacts\screenshot-baselines.json
```

Latest result:

```text
GCS screenshot baseline checks passed (1 baselines)
```

## What The Screenshot Shows

- a compact model canvas for the `g1` scene;
- an evidence rail for accepted status, warning status, commit, and version
  advance;
- D2 diagnostic-classification counts;
- D3 replay timeline stages;
- a research boundary that distinguishes static evidence from live GUI
  behavior.

## Acceptance

- The screenshot is generated from repository evidence artifacts.
- The manifest records dimensions, byte count, and sha256.
- The screenshot baseline checker passes.
- The package explicitly says it is not live GUI evidence.

## Next Upgrade

Turn this static package into a live D5 workbench walkthrough only when the
viewer can project report evidence without becoming hidden solver truth.
