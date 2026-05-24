# P4 Scientific Figure Pipeline Phase Close

Snapshot date: 2026-05-24.

Governing conventions:

- **GCS Scientific Figure Pipeline**
- **GCS Warm Evidence Tokens**
- **GCS Visual Integrity Gate**
- **GCS Art Director Review**

## Phase Result

P4 is closed.

The project now has a repo-native production path for dense execution-map
figures:

1. semantic figure spec;
2. shared evidence-token theme;
3. layout-aware HTML/CSS compositor;
4. browser-rendered review artifacts;
5. token lint;
6. structural figure QA;
7. completed-task archive and process learning.

Figure 71 is the phase proof. It now displays a browser-rendered review PNG in
`docs/architecture/71-step-1-40-execution-report.md`, while the old
coordinate-drawn SVG is retained only as historical prototype.

## Completed Steps

| Step | Result | Evidence |
| --- | --- | --- |
| P4.1 | Execution-map spec schema stabilized with canonical token fields. | `execution-map-spec-schema.md`, `figure71.yaml`, `figure_qa.py` |
| P4.2 | Browser export smoke added for review PNG/PDF artifacts. | `browser_export.py`, manifest, review artifacts |
| P4.3 | Graph/chart backends deferred by third-party governance decision. | `84-p4-3-graph-chart-backend-decision.md` |
| P4.4 | Figure 71 rebuilt through the repo-native pipeline and old SVG demoted. | `85-p4-4-execution-map-rebuild.md` |

## Stable Decisions

- Dense figures start from semantic specs, not exported SVG edits.
- `figure1.theme.json` remains the current editorial seed for figure colors.
- Figure renderers should not introduce raw hex values outside token sources.
- P4.4 does not need graph/chart dependencies.
- Browser review artifacts are useful, but browser-process reliability still
  needs later screenshot-baseline work.
- Figma MCP remains deferred until after repo-native visual integrity gates and
  showcase work make the external value clear.

## Residual Risks

- Text overflow, overlap, and contrast are only partially covered by structural
  QA. P5.2 and P5.3 must make those gates measurable.
- Browser CLI behavior can vary by workstation. P4.4 added manifest refresh
  for existing artifacts, but P5.4 should decide a stable screenshot baseline
  backend.
- Figure 71 proves the pipeline on one dense execution-map figure; P6 should
  prove it on an integrated showcase with geometry, rank, gluing, diagnostics,
  and obstruction variants.

## Downstream Plan

Next phase focus:

1. P5.2: add rendered text overflow checks.
2. P5.3: add overlap and contrast checks.
3. P5.4: add screenshot baselines.
4. P6.1-P6.3: define and produce an integrated showcase.
5. P6.4: decide whether Figma MCP adds value after repo-native gates are
   stable.

## Phase-Close Acceptance

P4 close is accepted because:

- each P4 step has a durable task/archive record;
- the execution-map figure has a spec, editable source, review artifacts, and
  QA evidence;
- dependency expansion was explicitly governed before rebuild;
- the next visual-integrity phase has concrete first steps.
