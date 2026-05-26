---
task_id: 2026-05-26-researcher-audience-narrative-stage
status: complete
request: "Advance all next-stage narrative-line tasks, set researchers as the primary audience, persist D1/D2 demos, release readiness, external comparison, benchmark criteria, governance eval seeds, narrative map updates, and push scoped changes."
scope: docs
risk: medium
owning_agent: gcs-architecture-steward
specialist_agents:
  - gcs-quality-steward
  - task-scoped-session-closer
affected_contracts:
  - none
affected_paths:
  - docs/architecture/
  - docs/product/
  - docs/agentic/
  - tools/architecture_visualization/specs/
required_evidence:
  - validate-task-card
  - validate-completed-task-report
  - validate-docs
  - validate-inventory
  - validate-skills
  - check-dependencies
  - score-closure-report
  - D1 CLI smoke transcript
  - D2 diagnostic classification transcript
human_gate_required: false
human_gate_reason: ""
---

# Researcher-Audience Narrative Stage

## Scope

Advance the weak narrative lines identified by the Figure 95 baseline:

- set `researchers` as the primary audience;
- create D1 and D2 demo packages with real command evidence;
- define release-readiness and package-smoke criteria;
- add external solver comparison and benchmark planning;
- add benchmark candidate selection criteria;
- add prompt-level governance eval seeds for E-GOV-001, E-GOV-002, and
  E-GOV-008;
- refresh narrative-map levels and Figure 95 baseline artifacts;
- close with validation, archive, scoped commit, and push.

## Non-Goals

- Do not change solver, runtime, IO, viewer, fixture, CMake, or test behavior.
- Do not promote any fixture into a benchmark corpus.
- Do not claim public release readiness.
- Do not stage unrelated `docs/research/OpusTime/OpusTime.md` or
  `docs/reports/report_/` work.

## Context To Read

- `docs/architecture/95-gcs-narrative-map.md`
- `docs/architecture/70-visualization/narrative-line-level-baseline-20260526.md`
- `docs/product/gcs-demo-ladder.md`
- `docs/product/gcs-product-user-brief.md`
- `docs/agentic/governance-eval-roadmap.md`
- `docs/architecture/96-fixture-corpus-maturity-ladder.md`
- `docs/architecture/50-implementation/third-party-policy.md`

## Acceptance Gates

- Primary audience is explicitly set to solver and geometric-constraint
  researchers.
- D1 and D2 demo packages include command evidence and limitations.
- Release readiness states current non-readiness and the evidence needed to
  cross the threshold.
- External comparison names source-grounded comparison targets and explains why
  GCS should be judged by evidence semantics, not CAD feature breadth.
- Benchmark criteria prevent unstable or unsupported fixtures from being
  marketed as benchmark wins.
- Governance eval seeds are concrete enough for future validator candidates.
- Narrative map and Figure 95 reflect the post-batch maturity changes.

## Verification Plan

```bat
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt --save-replay-evidence docs\product\demos\d1-cli-smoke\artifacts\g1-replay-evidence.report.json
out\build\clang-ninja\GCS.exe fixtures\scene\verification\lgs\well_constrained.txt
out\build\clang-ninja\GCS.exe fixtures\scene\verification\lgs\under_constrained.txt
out\build\clang-ninja\GCS.exe fixtures\scene\verification\lgs\over_constrained.txt
out\build\clang-ninja\GCS.exe fixtures\scene\verification\io\malformed.txt
out\build\clang-ninja\GCS.exe fixtures\scene\counterexamples\mixed_geometry_20g40c_singular_20260524.gcs.json
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-researcher-audience-narrative-stage.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-researcher-audience-narrative-stage\README.md
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-inventory
python tools\agentic_design\agentic_toolkit.py validate-skills
python tools\agentic_design\agentic_toolkit.py check-dependencies
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-26-researcher-audience-narrative-stage\README.md --min-score 30
```

## Evidence Bundle

Command evidence collected before and during writing:

- D1 `g1.txt` CLI smoke returned `Status: AcceptedWithWarnings`,
  `Accepted: true`, and `gluing.accepted`.
- D1 replay report generation initially failed without elevated write access,
  then succeeded after writing the demo artifact path with appropriate access.
- D2 over-constrained fixture returned nonzero as expected with
  `Status: Failed` and `runtime.numeric_failure`.
- D2 malformed IO fixture returned nonzero as expected with
  `io.parse.entity_count`.
- D2 singular counterexample returned nonzero as expected with
  `Status: NumericallySingular` and
  `runtime.post_local_diagnostics_blocked`.
- Figure 95 SVG parsed as XML and the refreshed PNG review render was visually
  checked for non-overlapping rows, labels, and callout text.
- `python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-researcher-audience-narrative-stage.md`
  passed.
- `python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-researcher-audience-narrative-stage\README.md`
  passed.
- `python tools\agentic_design\agentic_toolkit.py validate-docs` passed.
- `python tools\agentic_design\agentic_toolkit.py validate-inventory` passed.
- `python tools\agentic_design\agentic_toolkit.py validate-skills` passed.
- `python tools\agentic_design\agentic_toolkit.py check-dependencies` passed.
- `python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-26-researcher-audience-narrative-stage\README.md --min-score 30`
  returned closure score `34/40` after final evidence insertion.

## Residual Risks

- D1/D2 demos are command-line evidence packages, not polished UI demos.
- External comparison is a benchmark plan and selection standard, not a
  completed benchmark run.
- Researcher audience strategy is a positioning decision; README/public
  distribution changes remain a future task.
- Figure 95 scores are visualization aids and should not replace textual review
  of narrative maturity.
