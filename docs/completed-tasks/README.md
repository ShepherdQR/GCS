# Completed Tasks

This directory stores durable records for completed project tasks. Each task
gets its own folder so the archive can grow without turning into a single
chronological scratchpad.

## Folder Contract

Use this shape for every completed task:

```text
docs/completed-tasks/
  YYYY-MM-DD-short-task-slug/
    README.md
    artifacts.md      # optional, when the task has many generated assets
    evidence.md       # optional, when validation output is worth preserving
```

The task `README.md` should answer:

- what problem the task solved;
- what durable files, scripts, docs, or assets were produced;
- what validation was run;
- what commits or branches matter;
- what follow-up work remains.

Do not store raw chat logs here. Preserve decisions, outputs, acceptance
evidence, and links to project files.

## Legacy Validation Policy

Completed-task reports use the S2-04 policy in
`docs/agentic/legacy-artifact-policy.md`.

Use these labels when deciding whether an archive belongs in an opt-in gate:

| Label | Meaning | Gate treatment |
| --- | --- | --- |
| `validator-clean` | Current or migrated report that passes the active completed-task validator. | Safe to include explicitly. |
| `migrated` | Older report updated because a new task depends on it as active evidence. | Include only after the migration is committed and recorded. |
| `legacy-exempt` | Useful historical report that predates the current validator shape. | Do not select by default. |
| `low-risk-no-archive` | Task intentionally allowed by the lifecycle runbook to remain chat-only or commit-note-only. | Missing archive is not a failure. |
| `parallel-session-pending` | Artifact owned by another active branch, worktree, or conversation. | Exclude from the current task's gate evidence. |

Do not migrate historical reports only to make the whole tree pass. Migrate an
older archive only when a new roadmap decision, E001 calibration,
institutional-agent promotion, or quality-gate decision depends on that record.

## Index

| Date | Task | Status |
| --- | --- | --- |
| 2026-05-26 | [Narrative map third-stage execution](2026-05-26-narrative-map-third-stage-execution/README.md) | done |
| 2026-05-26 | [Institutional process AI token economics](2026-05-26-institutional-process-ai-token-economics/README.md) | done |
| 2026-05-26 | [Researcher evidence roadmap execution](2026-05-26-researcher-evidence-roadmap-execution/README.md) | done |
| 2026-05-26 | [Researcher-audience narrative stage](2026-05-26-researcher-audience-narrative-stage/README.md) | done |
| 2026-05-26 | [Task-scoped session closer skill upgrade](2026-05-26-task-scoped-session-closer-skill-upgrade/README.md) | done |
| 2026-05-26 | [Repository audit session closeout](2026-05-26-repository-audit-session-closeout/README.md) | done |
| 2026-05-26 | [Repository audit plan execution](2026-05-26-repository-audit-plan-execution/README.md) | done |
| 2026-05-26 | [UI viewer figure integration](2026-05-26-ui-viewer-figure-integration/README.md) | done |
| 2026-05-26 | [VE-002 viewer visual evidence](2026-05-26-ve002-viewer-visual-evidence/README.md) | done |
| 2026-05-26 | [UI viewer figure development plan](2026-05-26-ui-viewer-figure-development-plan/README.md) | done |
| 2026-05-26 | [AI organization narrative execution](2026-05-26-ai-organization-narrative-execution/README.md) | done |
| 2026-05-26 | [Next-stage mainline evidence](2026-05-26-next-stage-mainline-evidence/README.md) | done |
| 2026-05-26 | [AI governance plan session closeout](2026-05-26-ai-governance-plan-session-closeout/README.md) | done |
| 2026-05-26 | [Repository audit snapshot registry](2026-05-26-repository-audit-snapshot-registry/README.md) | done |
| 2026-05-26 | [Narrative plan execution](2026-05-26-narrative-plan-execution/README.md) | done |
| 2026-05-26 | [AI organization frontier research](2026-05-26-ai-organization-frontier-research/README.md) | done |
| 2026-05-26 | [Repository audit next steps execution](2026-05-26-repository-audit-next-steps-execution/README.md) | done |
| 2026-05-26 | [Repository audit diff mode](2026-05-26-repository-audit-diff-mode/README.md) | done |
| 2026-05-26 | [Repository audit overview and session efficiency](2026-05-26-repository-audit-overview-and-session-efficiency/README.md) | done |
| 2026-05-26 | [Repository audit collector MVP](2026-05-26-repository-audit-collector-mvp/README.md) | done |
| 2026-05-26 | [Git stitch and PR audit permission policy](2026-05-26-git-stitch-pr-audit-permission-policy/README.md) | done |
| 2026-05-26 | [Git session branch session summary](2026-05-26-git-session-branch-session-summary/README.md) | done |
| 2026-05-26 | [Tailor Git session timeline cleanup](2026-05-26-tailor-git-session-timeline-cleanup/README.md) | done |
| 2026-05-27 | [Claude Code agent & skill ecosystem upgrade](2026-05-27-claude-code-agent-skill-upgrade/README.md) | done |
| 2026-05-25 | [Agentic governance execution](2026-05-25-agentic-governance-execution/README.md) | done |
| 2026-05-25 | [Agentic PR governance and nightly diagnostics](2026-05-25-agentic-pr-governance-nightly-diagnostics/README.md) | done |
| 2026-05-25 | [Agentic-SE next direction closeout](2026-05-25-agentic-se-next-direction-closeout/README.md) | done |
| 2026-05-25 | [S2-05 Agentic default gate decision](2026-05-25-s2-05-agentic-default-gate-decision/README.md) | done |
| 2026-05-25 | [S2-04 legacy artifact policy](2026-05-25-s2-04-legacy-artifact-policy/README.md) | done |
| 2026-05-25 | [Repository audit statistics architecture](2026-05-25-repository-audit-statistics-architecture/README.md) | done |
| 2026-05-25 | [UI workbench session closeout](2026-05-25-ui-workbench-session-closeout/README.md) | done |
| 2026-05-25 | [UI Phase 7 diagnostics overlay](2026-05-25-ui-phase7-diagnostics-overlay/README.md) | done |
| 2026-05-25 | [GCS commercial architecture and behavior model update](2026-05-25-gcs-commercial-architecture-behavior-model/README.md) | done |
| 2026-05-25 | [UI Phase 6 focus projection](2026-05-25-ui-phase6-focus-projection/README.md) | done |
| 2026-05-25 | [Agentic SE roadmap items 1, 2, 3, and 5](2026-05-25-agentic-se-roadmap-items-1-2-3-5/README.md) | done |
| 2026-05-25 | [GCS solver UI requirements architecture](2026-05-25-gcs-solver-ui-requirements-architecture/README.md) | done |
| 2026-05-25 | [LGS spanning-tree method research](2026-05-25-lgs-spanning-tree-method-research/README.md) | done |
| 2026-05-25 | [S4-05 institutional-agent reassessment](2026-05-25-s4-05-institutional-agent-reassessment/README.md) | done |
| 2026-05-25 | [S3-04 E001 skill promotion decision](2026-05-25-s3-04-e001-skill-promotion-decision/README.md) | done |
| 2026-05-25 | [S2-01 opt-in gate policy](2026-05-25-s2-01-opt-in-gate-policy/README.md) | done |
| 2026-05-25 | [Step 50 replay evidence workflow review](2026-05-25-step-50-replay-evidence-workflow-review/README.md) | done |
| 2026-05-25 | [S1-04 low-risk chat-only boundary](2026-05-25-s1-04-low-risk-chat-only-boundary/README.md) | done |
| 2026-05-25 | [S3-02 negative E001 eval](2026-05-25-s3-02-negative-e001-eval/README.md) | done |
| 2026-05-25 | [Repository cleanup and scene fixture hygiene](2026-05-25-repository-cleanup-scene-fixture-hygiene/README.md) | done |
| 2026-05-24 | [Agentic lifecycle Step 47-49 session archive](2026-05-24-agentic-lifecycle-step-47-49-session/README.md) | done |
| 2026-05-24 | [Git worktree protocol](2026-05-24-git-worktree-protocol/README.md) | done |
| 2026-05-24 | [S1-05 and Step 49 replay report artifact](2026-05-24-s1-05-step-49-replay-report-artifact/README.md) | done |
| 2026-05-24 | [Step 48 replay consumer and S1-03 checklist](2026-05-24-step-48-replay-consumer-and-s1-03-checklist/README.md) | done |
| 2026-05-24 | [UI aesthetic pipeline dialogue archive](2026-05-24-ui-aesthetic-pipeline-dialogue-archive/README.md) | done |
| 2026-05-24 | [P6.4 Figma MCP decision](2026-05-24-p6-4-figma-mcp-decision/README.md) | done |
| 2026-05-24 | [P6.3 showcase figure pipeline](2026-05-24-p6-3-showcase-figure-pipeline/README.md) | done |
| 2026-05-24 | [P6.2 showcase fixture evidence](2026-05-24-p6-2-showcase-fixture-evidence/README.md) | done |
| 2026-05-24 | [P6.1 integrated showcase brief](2026-05-24-p6-1-integrated-showcase-brief/README.md) | done |
| 2026-05-24 | [P5 visual integrity phase close](2026-05-24-p5-visual-integrity-phase-close/README.md) | done |
| 2026-05-24 | [P5.4 screenshot baselines](2026-05-24-p5-4-screenshot-baselines/README.md) | done |
| 2026-05-24 | [P5.3 overlap and contrast gates](2026-05-24-p5-3-overlap-contrast-gates/README.md) | done |
| 2026-05-24 | [P5.2 text overflow gate](2026-05-24-p5-2-text-overflow-gate/README.md) | done |
| 2026-05-24 | [P4 scientific figure pipeline phase close](2026-05-24-p4-scientific-figure-pipeline-phase-close/README.md) | done |
| 2026-05-24 | [P4.4 execution-map figure rebuild](2026-05-24-p4-4-execution-map-rebuild/README.md) | done |
| 2026-05-24 | [P4.3 graph/chart backend decision](2026-05-24-p4-3-graph-chart-backend-decision/README.md) | done |
| 2026-05-24 | [P5.1 token lint gate](2026-05-24-p5-1-token-lint-gate/README.md) | done |
| 2026-05-24 | [Step 47 runtime replay evidence export](2026-05-24-step-47-runtime-replay-evidence-export/README.md) | done |
| 2026-05-24 | [Scene auto explorer design, implementation, and next-phase plan](2026-05-24-scene-auto-explorer-design-implementation-plan/README.md) | done |
| 2026-05-24 | [Step 41-46 execution and dialogue archive](2026-05-24-step-41-46-execution-and-dialogue-archive/README.md) | done |
| 2026-05-24 | [Agentic SE four-phase PDCA bootstrap](2026-05-24-agentic-se-four-phase-pdca/README.md) | done |
| 2026-05-24 | [GCS architecture rewrite blueprint](2026-05-24-gcs-architecture-rewrite-blueprint/README.md) | done |
| 2026-05-24 | [GCS architecture visualization and SVG editing workflow](2026-05-24-gcs-architecture-visualization-svg-workflow/README.md) | done |
| 2026-05-24 | [Generated constraint model library](2026-05-24-generated-constraint-model-library/README.md) | done |
| 2026-05-24 | [Agentic operating layer and rank evidence](2026-05-24-agentic-operating-layer-rank-evidence/README.md) | done |
| 2026-05-24 | [Agentic SE experience library](2026-05-24-agentic-se-experience-library/README.md) | done |
| 2026-05-24 | [E001 deep research expansion](2026-05-24-e001-deep-research-expansion/README.md) | done |
| 2026-05-24 | [E001 executable closure tooling](2026-05-24-e001-executable-closure-tooling/README.md) | done |
| 2026-05-24 | [E001 dialogue summary and archive](2026-05-24-e001-dialogue-summary-and-archive/README.md) | done |
| 2026-05-24 | [E002 phase-step research and tooling session](2026-05-24-e002-phase-step-research-tooling-session/README.md) | done |
| 2026-05-24 | [Git branch consolidation session](2026-05-24-git-branch-consolidation-session/README.md) | done |
| 2026-05-24 | [UI design development plan and session archive](2026-05-24-ui-design-development-plan-and-session-archive/README.md) | done |
