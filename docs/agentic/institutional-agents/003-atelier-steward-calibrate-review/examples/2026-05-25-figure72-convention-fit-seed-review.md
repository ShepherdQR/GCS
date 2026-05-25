# Figure 72 Convention Fit Seed Review

Date: 2026-05-25

Role: `Atelier Steward: Calibrate-Review`

Status: conditional-fit

Role maturity effect: seed-example-only

## Source Scope

- Request: create the first real visual-review artifact package for I003/I004
  while keeping both roles seed and avoiding mainline roadmap/tool conflicts.
- Artifact under review:
  - `docs/architecture/70-visualization/assets/figure72-gcs-integrated-showcase-scene.html`
- Source evidence:
  - `docs/architecture/88-p6-1-integrated-showcase-brief.md`
  - `tools/architecture_visualization/specs/figure72.yaml`
  - `docs/architecture/91-p6-4-figma-mcp-decision.md`
  - `docs/architecture/75-ui-design-system-conventions.md`
  - `docs/architecture/76-ui-design-system-execution-plan.md`
- Files intentionally out of scope:
  - `docs/agentic/agile-pdca-roadmap.md`
  - `docs/completed-tasks/README.md`
  - tool code

## Governing Conventions

| Convention | Applies? | Evidence |
| --- | --- | --- |
| GCS Quiet Technical Atelier | yes | The Figure 72 brief asks for a warm, precise, calm showcase centered on solver evidence. |
| GCS Warm Evidence Tokens | yes | `figure72.yaml` maps all seven panels to canonical `evidence.*` tokens. |
| GCS Evidence-First Interface Grammar | yes | Panels expose scene contract, graph, boundary, numeric rank/residual, diagnostics, rejection, and gate-chain evidence. |
| GCS Scientific Figure Pipeline | yes | Figure 72 has a semantic spec and tokenized HTML production artifact. |
| GCS Visual Integrity Gate | yes | The spec names token lint, fixture evidence, compositor freshness, text overflow, and overlap/contrast gates. |
| GCS Art Director Review | yes | P6.4 names Art Director review as the next repo-native review step before reopening external design tooling. |

## Evidence Read

| Evidence | Observation | Confidence |
| --- | --- | --- |
| P6.1 brief | The five-second claim and required panel list are explicit. | high |
| Figure 72 spec | The spec uses `gcs.showcase_figure.v1`, seven panels, canonical tokens, and named default gates. | high |
| Figure 72 HTML | The artifact includes title, subtitle, status, panel boxes, text budgets, contrast markers, and semantic panel classes. | medium |
| P6.4 decision | Figma MCP is deferred; repo-native review artifacts and Art Director review are the next path. | high |

## Fit Findings

| Priority | Convention | Finding | Required action |
| --- | --- | --- | --- |
| P1 | GCS Art Director Review | The artifact is fit to enter independent visual review, but this steward review is not that final taste judgment. | Run I004 Art Director review on the rendered HTML or browser output before final showcase use. |
| P2 | GCS Visual Integrity Gate | Source-level markers exist; final visual proof is stronger after browser PNG/PDF export and screenshot baseline if reproducible. | Keep P7.1/P7.2 as downstream review work rather than folding it into this seed-package change. |
| P2 | GCS Scientific Figure Pipeline | The source-of-truth path is spec -> metadata -> HTML, which matches the adopted production direction. | Preserve the HTML/spec path; do not introduce Figma or hand-edited bitmap work here. |
| P3 | GCS Evidence-First Interface Grammar | Evidence roles are visible in panel taxonomy; the `AcceptedWithWarnings` state should remain legible as warning-context, not pure success. | Art Director review should check whether the status pill reads with enough nuance in the rendered artifact. |

## Boundary Check

- Solver/runtime truth remains outside UI/viewer artifacts: yes.
- Generated artifacts are rebuildable from repo sources: yes, according to the
  Figure 72 spec and compositor path.
- Dense text uses layout-aware composition rather than coordinate-only labels:
  yes for the HTML review path.

## Decision

Conditional fit.

Rationale: Figure 72 has enough concrete evidence to justify a real seed
example for the Atelier Steward. The review should not be treated as final
visual approval because the independent Art Director pass and any rendered
PNG/PDF review artifact remain downstream work.

## Commit Boundary

- Recommended commit scope: I003/I004 prompt, template, eval, and example
  files only.
- Files that should not be included: roadmap, completed-task index, tool code,
  generated Figure 72 artifacts.
- Follow-up owner: mainline visual-review or P7 worker.

## Role Status

This is one real seed example for I003. It does not upgrade the role to
practiced.
