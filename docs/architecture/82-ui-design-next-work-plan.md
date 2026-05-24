# UI Design Next Work Plan

Snapshot date: 2026-05-24.

This note persists the current forward plan after P4.1. It records the work
remaining after the execution-map schema stabilization and states the preferred
order for the next aesthetic/design-system work.

Governing conventions:

- **GCS Quiet Technical Atelier**
- **GCS Warm Evidence Tokens**
- **GCS Evidence-First Interface Grammar**
- **GCS Scientific Figure Pipeline**
- **GCS Visual Integrity Gate**
- **GCS Art Director Review**

## Current State

Completed:

- P2 Token Unification is closed.
- P3 Viewer UI Implementation is closed.
- P4.1 is complete: execution-map specs now have `gcs.execution_map.v1`,
  `expected_step_range`, `token_taxonomy`, and per-arc `canonical_token`
  fields.
- P4.2 is complete: Figure 71 can run a browser export smoke through a local
  Chromium CLI, producing a manifest plus review PNG/PDF artifacts when browser
  tooling is available.
- P5.1 is complete: token lint now prevents raw hex drift outside approved
  token sources and fails unknown token references before asset rebuilds.
- P4.3 is complete: graph/chart backends are deferred for P4.4, so no new
  renderer dependency is approved before the execution-map asset rebuild.
- P4.4 is complete: Figure 71 is displayed from the browser-rendered review
  PNG, with editable HTML, review PDF, manifest, QA evidence, and old SVG
  prototype demotion recorded.
- P4 is closed: the scientific figure pipeline has a phase-close summary and
  downstream visual-integrity plan.
- P5.2 is complete: generated Figure 71 HTML now carries explicit text budgets
  and the default quality gates include text overflow checks.
- P5.3 is complete: generated Figure 71 HTML now carries layout-box and
  contrast markers, with forced overlap and weak-contrast fixtures in tests.
- P5.4 is complete: Figure 71 now has a stable screenshot-baseline manifest,
  exact PNG artifact checks, and forced baseline failure fixtures.
- P5 is closed: default visual-integrity gates and reviewer-only art-direction
  gates are now separated before P6.
- P6.1 is complete: the integrated showcase brief now names the claim, source
  evidence, token vocabulary, panels, and review questions.
- P6.2 is complete: showcase metadata now carries executable fixture evidence
  for rank/residual, gluing, diagnostics, replay boundary, panels, tokens, and
  negative rejection.
- P6.3 is complete: Figure 72 now has a tokenized HTML production artifact and
  default visual-integrity coverage.
- P6.4 is complete: Figma MCP is deferred, with only a future explicit pilot
  allowed if a concrete collaboration/editable-layout gap appears.

Active phase:

- Post-P6 aesthetic review and Figure 72 review artifact hardening.

## Persisted Forward Plan

| Order | Work | Status | Purpose | Acceptance |
| --- | --- | --- | --- | --- |
| 1 | P4.2 Browser-rendered export path | Done | Export tokenized HTML figures to reviewable image/PDF artifacts when browser tooling is available. | Browser smoke renders the figure and proves `--gcs-*` variables survive export. |
| 2 | P5.1 Token lint gate | Done | Enforce the P2/P3 rule that raw hex values belong only in token sources and unknown tokens fail fast. | Forced raw-hex fixture fails; current code passes. |
| 3 | P4.3 Graph/chart backend decision | Done | Decide whether execution-map panels need new graph/chart backends or can stay repo-native for now. | Dependency decision recorded before any new renderer package is added. |
| 4 | P4.4 Rebuild execution-map figure | Done | Regenerate execution-map assets through the stable spec/compositor/QA path and demote old SVG output to prototype history. | `figure_qa.py` passes and generated artifacts are linked from architecture docs. |
| 5 | P4 phase close | Done | Reassess whether repo-native figure production is stable enough before considering Figma MCP. | Phase-close summary and downstream plan update committed. |
| 6 | P5.2 Text overflow gate | Done | Catch text that would spill from figure panels or compact UI surfaces. | Forced overflow fixture fails. |
| 7 | P5.3 Overlap and contrast gates | Done | Catch critical text/shape overlap and weak contrast in status/evidence surfaces. | Forced overlap fails and contrast report is produced. |
| 8 | P5.4 Screenshot baselines | Done | Add stable visual baselines for core GUI and figure states. | Baseline policy and first stable screenshots exist. |
| 9 | P5 phase close | Done | Decide default versus reviewer-only visual-integrity gates before P6. | Phase-close summary and downstream plan update committed. |
| 10 | P6.1 Showcase brief | Done | Define the integrated feature constraint graph showcase using canonical evidence vocabulary. | Brief review passes. |
| 11 | P6.2 Showcase fixture | Done | Promote or generate a showcase scene with rank, gluing, replay, and diagnostic evidence. | Public solver/report gate passes. |
| 12 | P6.3 Showcase figure | Done | Produce the showcase through the scientific figure pipeline and tokenized compositor. | Visual integrity QA passes. |
| 13 | P6.4 Figma MCP decision | Done | Decide whether external design-surface review adds enough value after repo-native QA is stable. | Governance decision recorded. |

## P4.2 Completion Summary

- Added a thin browser export smoke rather than a broad rendering framework.
- Used local Chrome/Edge/Chromium CLI discovery, with a skipped manifest when
  browser tooling is not available.
- Produced Figure 71 review PNG/PDF artifacts in this environment and recorded
  token proof in `figure71-gcs-step-1-40-browser-export.json`.
- Extended figure QA so browser smoke evidence is checked through the spec.

## P5.1 Completion Summary

- Added `tools/ui_qa/gcs_token_lint.py` to scan viewer, figure-renderer, and UI
  QA code for raw hex values outside approved token sources.
- Added AST checks for string-literal references to unknown `GCS_TOKENS`,
  `GCS_THEME`, `STATE_COLORS`, and renderer `COLORS` keys.
- Added figure-spec checks for unknown `canonical_token` values.
- Replaced renderer fallback color dictionaries with theme loading from
  `figure1.theme.json`.
- Added unit tests for current-repo pass, forced raw-hex failure, forced token
  failure, and forced spec-token failure.
- Promoted `python.gcs_token_lint` and `python.gcs_token_lint_tests` into the
  default agentic quality-gate sequence.

## P4.3 Completion Summary

- Added `docs/architecture/84-p4-3-graph-chart-backend-decision.md`.
- Deferred external graph/chart backends for P4.4.
- Recorded that future Graphviz/D2/ELK/Vega-style candidates need dependency
  metadata, provider order, offline behavior, CMake or CLI boundary, and audit
  gates before adoption.
- Preserved the immediate P4.4 path as repo-native semantic spec, theme,
  HTML/CSS compositor, browser smoke, figure QA, and token lint.

## P4.4 Completion Summary

- Updated `71-step-1-40-execution-report.md` to display
  `figure71-gcs-step-1-40-evidence-map.review.png`.
- Kept the editable HTML, review PDF, browser manifest, and Figure 71 QA JSON
  as first-class linked artifacts.
- Retained `figure71-gcs-step-1-40-evidence-map.svg` only as a historical
  prototype.
- Added `--reuse-existing-artifacts` to `browser_export.py` for truthful
  manifest refresh when browser artifacts exist but a local browser process
  does not exit cleanly.

## P4 Phase-Close Summary

- Added `docs/architecture/86-p4-scientific-figure-pipeline-phase-close.md`.
- Closed P4 with Figure 71 as the phase proof: semantic spec, shared theme,
  HTML/CSS compositor, browser-rendered review artifacts, token lint, and
  structural QA.
- Recorded residual risks for P5: text overflow, overlap, contrast, and
  screenshot-baseline stability.

## P5.2 Completion Summary

- Added `tools/ui_qa/gcs_text_overflow.py`.
- Added Figure 71 text-budget markers in the HTML compositor and regenerated
  the HTML artifact.
- Added forced overflow and missing-budget tests.
- Promoted `python.gcs_text_overflow` and
  `python.gcs_text_overflow_tests` into the default quality-gate sequence.

## P5.3 Completion Summary

- Added `tools/ui_qa/gcs_overlap_contrast.py`.
- Added Figure 71 layout-box and contrast markers in the HTML compositor and
  regenerated the HTML artifact.
- Added forced overlap, weak contrast, and missing-marker tests.
- Promoted `python.gcs_overlap_contrast` and
  `python.gcs_overlap_contrast_tests` into the default quality-gate sequence.

## P5.4 Completion Summary

- Added `docs/architecture/70-visualization/assets/screenshot-baselines.json`
  with Figure 71's browser-rendered review PNG as the first stable baseline.
- Added `tools/ui_qa/gcs_screenshot_baseline.py` to validate PNG signature,
  dimensions, byte count, minimum byte count, and SHA256 digest.
- Added forced missing-file, dimension-mismatch, and digest-mismatch tests.
- Promoted `python.gcs_screenshot_baseline` and
  `python.gcs_screenshot_baseline_tests` into the default quality-gate
  sequence.
- Added `docs/architecture/70-visualization/screenshot-baseline-gate.md`.

## P5 Phase-Close Summary

- Added `docs/architecture/87-p5-visual-integrity-phase-close.md`.
- Closed P5 with token lint, text overflow, overlap/contrast, and screenshot
  baselines as default quality gates.
- Recorded that main-claim clarity, editorial hierarchy, and external
  design-tool value remain reviewer-only art-direction gates.
- Moved the active phase to P6 and made P6.1 the next implementation step.

## P6.1 Completion Summary

- Added `docs/architecture/88-p6-1-integrated-showcase-brief.md`.
- Defined the five-second claim, audience, source evidence, canonical evidence
  vocabulary, required panels, production direction, and Art Director review
  questions.
- Required the negative missing-fixed variant to remain visible in showcase
  work.
- Kept fixture and figure assets unchanged so P6.2 can promote evidence before
  P6.3 changes visuals.

## P6.2 Completion Summary

- Enriched `fixtures/scene/showcase/integrated_feature_showcase.metadata.json`
  and the missing-fixed negative metadata with P6.1 panel, token, rank,
  residual, gluing, diagnostic, replay-boundary, and rejection evidence.
- Added `tools/architecture_visualization/showcase_fixture_evidence.py`.
- Added forced missing-panel, rank-mismatch, and report-code mismatch tests.
- Promoted `python.showcase_fixture_evidence` and
  `python.showcase_fixture_evidence_tests` into default quality gates.
- Added `docs/architecture/89-p6-2-showcase-fixture-evidence.md`.

## P6.3 Completion Summary

- Added `tools/architecture_visualization/specs/figure72.yaml`.
- Added `tools/architecture_visualization/showcase_scene_html_compositor.py`
  and generated
  `docs/architecture/70-visualization/assets/figure72-gcs-integrated-showcase-scene.html`.
- Extended Figure 72 into the default text-overflow and overlap/contrast
  checks.
- Promoted compositor freshness and tests into default quality gates.
- Updated the architecture atlas to make HTML the P6.3 production path, while
  preserving the existing SVG as a legacy atlas artifact.

## P6.4 Completion Summary

- Added `docs/architecture/91-p6-4-figma-mcp-decision.md`.
- Checked official Figma MCP documentation for remote and desktop server
  guidance.
- Deferred install/configuration now because Figure 72 already has a
  repo-native HTML production path and default visual-integrity gates.
- Recorded future pilot conditions: official provider choice, data boundary,
  write policy, artifact comparison, rollback plan, and offline gate
  preservation.

## Updated Next Move

The next implementation step should be **Figure 72 Browser Review Baseline**.

Reasoning:

- P4.2 proved HTML-to-review-artifact export is feasible.
- P5.1 now guards token drift before any final asset rebuild.
- P4.3 now confirms P4.4 should not add graph/chart dependencies.
- P4.4 rebuilt the execution-map display artifact and recorded the remaining
  browser-process caveat.
- P4 is now closed, so downstream visual-integrity work can begin from an
  explicit phase summary.
- P5.2 is now in place as a source-level text-budget gate.
- P5.3 is now in place as a source-level overlap and contrast gate.
- P5.4 is now in place as an artifact-level screenshot baseline gate.
- P5 is closed, so showcase work can now use a known default/reviewer-only
  visual-integrity boundary.
- P6.1 now defines the main claim, evidence vocabulary, panels, and review
  gates.
- P6.2 now makes the showcase fixture evidence directly consumable by P6.3
  figure production.
- P6.3 upgraded the Figure 72 production path against the brief, enriched
  metadata, and P5 visual-integrity gates.
- P6.4 now defers Figma MCP and names the repo-native next review path.
- Figure 72 should gain a browser PNG/PDF review artifact and screenshot
  baseline before external design tooling is reconsidered.

## Post-P6 Forward Plan

The next plan is **P7 Review Artifact Hardening**.

| Order | Work | Status | Purpose | Acceptance |
| --- | --- | --- | --- | --- |
| 14 | P7.1 Figure 72 browser review baseline | Next | Export Figure 72 HTML into PNG/PDF review artifacts and baseline the stable PNG if reproducible. | Browser export evidence and screenshot-baseline manifest entry, or a documented skip reason. |
| 15 | P7.2 Art Director review | Pending | Judge Figure 72 against five-second claim clarity, evidence hierarchy, text economy, semantic color, and GCS Quiet Technical Atelier. | Approval, conditional approval, or rejection with findings. |
| 16 | P7.3 Atlas/report hardening | Pending | Make Figure 72 review artifacts first-class in the atlas and keep the legacy SVG clearly secondary. | Atlas/report links and visual gates pass. |
| 17 | P7.4 Figma pilot gate | Pending | Reopen Figma MCP only if P7.2/P7.3 names a concrete collaboration, editable-layout, or external-review gap. | Pilot request with provider, data boundary, write policy, rollback, and offline-gate plan, or explicit continued deferral. |

Operating rule:

- Continue the phase-step loop: task card -> execution plan -> implementation
  -> validation -> completed-task archive -> roadmap update -> Bladesmith
  learning -> commit -> continue.
- Keep Figure 72 HTML, metadata, and visual-integrity gates as the source of
  truth.
- Keep Figma MCP out of default build/test/QA paths unless a future pilot is
  explicitly accepted.

## Opportunistic Cleanup

P0 still has useful documentation cleanup:

- P0.2: cross-link `72-ui-aesthetic-roadmap.md`,
  `73-gcs-visual-taste-guide.md`, and
  `74-scientific-figure-production-paradigm.md` to the convention names in
  `75-ui-design-system-conventions.md`.
- P0.3: decide whether `75-ui-design-system-conventions.md` is enough as the
  design-system entry point or whether `70-visualization/` needs a short index.

This cleanup should be done when it helps orientation, but it should not block
P4/P5 implementation work.

## Preferred Working Bias

I prefer the following operating order:

1. Keep P4.2 closed as a thin browser-export smoke, not a large export
   framework.
2. Keep P5.1 token lint in the default quality-gate path before P4.4 rebuilds.
3. Decide P4.3 as a governance step, then rebuild the execution-map assets in
   P4.4 with token lint and QA already guarding the output.
4. Continue with P5.2/P5.3/P5.4 before spending time on showcase polish.
5. Delay Figma MCP until the repo-native pipeline can already produce clean,
   QA-backed artifacts.

Reasoning:

- P4.2 unblocks real export evidence, but it can grow too large if we try to
  solve every format at once.
- P5.1 is cheap and protects every later figure/UI step from drifting back into
  scattered raw colors.
- P4.4 should not happen before the basic gates exist; otherwise we may create
  impressive artifacts that are still fragile.
- P6 can now begin from a figure pipeline and visual integrity gate strong
  enough that showcase work is editorial polish, not manual rescue.

## Not Recommended Yet

- Do not install or configure Figma MCP as the next move.
- Do not introduce a new graph/chart package before P4.3 records the dependency
  decision.
- Do not install Figma MCP unless a future pilot request records a concrete
  collaboration, editable-layout, or review gap that the repo-native HTML
  pipeline does not cover.
