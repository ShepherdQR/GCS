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

Active phase:

- P4 Scientific Figure Pipeline.

## Persisted Forward Plan

| Order | Work | Status | Purpose | Acceptance |
| --- | --- | --- | --- | --- |
| 1 | P4.2 Browser-rendered export path | Done | Export tokenized HTML figures to reviewable image/PDF artifacts when browser tooling is available. | Browser smoke renders the figure and proves `--gcs-*` variables survive export. |
| 2 | P5.1 Token lint gate | Next | Enforce the P2/P3 rule that raw hex values belong only in token sources and unknown tokens fail fast. | Forced raw-hex fixture fails; current code passes. |
| 3 | P4.3 Graph/chart backend decision | Pending | Decide whether execution-map panels need new graph/chart backends or can stay repo-native for now. | Dependency decision recorded before any new renderer package is added. |
| 4 | P4.4 Rebuild execution-map figure | Pending | Regenerate execution-map assets through the stable spec/compositor/QA path and demote old SVG output to prototype history. | `figure_qa.py` passes and generated artifacts are linked from architecture docs. |
| 5 | P4 phase close | Pending | Reassess whether repo-native figure production is stable enough before considering Figma MCP. | Phase-close summary and downstream plan update committed. |
| 6 | P5.2 Text overflow gate | Pending | Catch text that would spill from figure panels or compact UI surfaces. | Forced overflow fixture fails. |
| 7 | P5.3 Overlap and contrast gates | Pending | Catch critical text/shape overlap and weak contrast in status/evidence surfaces. | Forced overlap fails and contrast report is produced. |
| 8 | P5.4 Screenshot baselines | Pending | Add stable visual baselines for core GUI and figure states. | Baseline policy and first stable screenshots exist. |
| 9 | P6.1 Showcase brief | Pending | Define the integrated feature constraint graph showcase using canonical evidence vocabulary. | Brief review passes. |
| 10 | P6.2 Showcase fixture | Pending | Promote or generate a showcase scene with rank, gluing, replay, and diagnostic evidence. | Public solver/report gate passes. |
| 11 | P6.3 Showcase figure | Pending | Produce the showcase through the scientific figure pipeline and tokenized compositor. | Visual integrity QA passes. |
| 12 | P6.4 Figma MCP decision | Pending | Decide whether external design-surface review adds enough value after repo-native QA is stable. | Governance decision recorded. |

## P4.2 Completion Summary

- Added a thin browser export smoke rather than a broad rendering framework.
- Used local Chrome/Edge/Chromium CLI discovery, with a skipped manifest when
  browser tooling is not available.
- Produced Figure 71 review PNG/PDF artifacts in this environment and recorded
  token proof in `figure71-gcs-step-1-40-browser-export.json`.
- Extended figure QA so browser smoke evidence is checked through the spec.

## Updated Next Move

The next implementation step should be **P5.1 Token Lint Gate**.

Reasoning:

- P4.2 proved HTML-to-review-artifact export is feasible.
- P4.4 should not rebuild the final execution-map asset set until token drift
  is guarded automatically.
- P4.3 can stay a small dependency decision and does not need to introduce a
  renderer package before token lint exists.

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
2. Do P5.1 token lint immediately after P4.2 and before P4.4 asset rebuild.
3. Then rebuild the execution-map assets in P4.4 with token lint and QA already
   guarding the output.
4. Continue with P5.2/P5.3 before spending time on showcase polish.
5. Delay Figma MCP until the repo-native pipeline can already produce clean,
   QA-backed artifacts.

Reasoning:

- P4.2 unblocks real export evidence, but it can grow too large if we try to
  solve every format at once.
- P5.1 is cheap and protects every later figure/UI step from drifting back into
  scattered raw colors.
- P4.4 should not happen before the basic gates exist; otherwise we may create
  impressive artifacts that are still fragile.
- P6 should wait until the figure pipeline and visual integrity gate are strong
  enough that showcase work is editorial polish, not manual rescue.

## Not Recommended Yet

- Do not install or configure Figma MCP as the next move.
- Do not introduce a new graph/chart package before P4.3 records the dependency
  decision.
- Do not regenerate final showcase assets before P5 has at least token lint and
  basic text/contrast checks.
