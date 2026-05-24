# P5 Visual Integrity QA Phase Close

Snapshot date: 2026-05-24.

Governing conventions:

- **GCS Visual Integrity Gate**
- **GCS Warm Evidence Tokens**
- **GCS Scientific Figure Pipeline**
- **GCS Art Director Review**

## Phase Result

P5 is closed.

The project now has an executable visual-integrity layer for repo-native UI and
figure work. The layer catches token drift, text overflow, declared layout
overlap, weak contrast, and changed screenshot review artifacts before P6
showcase work begins.

Figure 71 is the phase proof. Its current production artifact family includes:

1. tokenized HTML source;
2. browser-rendered review PNG/PDF;
3. text-budget markers;
4. layout-box and contrast markers;
5. screenshot-baseline manifest;
6. default quality-gate coverage for all of the above.

## Completed Steps

| Step | Result | Evidence |
| --- | --- | --- |
| P5.1 | Token lint prevents raw hex drift and unknown token references. | `gcs_token_lint.py`, forced raw-hex/token fixtures |
| P5.2 | Text overflow budgets make dense figure text measurable. | `gcs_text_overflow.py`, forced overflow fixture |
| P5.3 | Layout boxes and contrast targets make declared panel overlap and contrast measurable. | `gcs_overlap_contrast.py`, forced overlap/contrast fixtures |
| P5.4 | Screenshot baseline manifest pins the first stable Figure 71 review PNG. | `gcs_screenshot_baseline.py`, exact PNG digest fixture |

## Default Gates

The following checks are default quality gates:

- `python.gcs_token_lint`
- `python.gcs_token_lint_tests`
- `python.gcs_text_overflow`
- `python.gcs_text_overflow_tests`
- `python.gcs_overlap_contrast`
- `python.gcs_overlap_contrast_tests`
- `python.gcs_screenshot_baseline`
- `python.gcs_screenshot_baseline_tests`
- `python.browser_export`
- `python.showcase_scene_renderer`
- `python.agentic_toolkit`

Rationale: these gates are deterministic, repo-native, and cheap enough to run
with the normal build/test/public-evidence chain.

## Reviewer-Only Gates

The following remain reviewer-only until a later step makes them executable:

- five-second main-claim clarity;
- whether the artifact feels like **GCS Quiet Technical Atelier** rather than
  generic process decoration;
- whether the evidence hierarchy is editorially persuasive;
- whether a screenshot change is an improvement, not merely different;
- whether Figma, slides, or external design surfaces add enough collaboration
  value to justify a new dependency boundary.

Rationale: these are taste and judgment checks. They should be named and
recorded, but not reduced to brittle heuristics before the showcase exists.

## Stable Decisions

- Visual token drift belongs in default quality gates.
- Generated dense figures must emit source-level text, layout, and contrast
  metadata when they become production artifacts.
- Stable review PNGs must be represented in a screenshot-baseline manifest
  before they are treated as durable display artifacts.
- Exact PNG hashes are acceptable for the first baseline family, but future
  perceptual or pixel-diff tooling should reuse the manifest instead of
  creating a parallel registry.
- Figma MCP remains deferred to P6.4 now that repo-native QA is strong enough
  to evaluate external design-tool value honestly.

## Residual Risks

- Figure 71 is still the primary dense-figure proof; P6 should prove the same
  system on an integrated showcase.
- Screenshot baselines are exact-hash checks, so legitimate rendering changes
  require deliberate baseline updates.
- GUI viewer screenshots are not yet represented in the manifest.
- Reviewer-only taste checks still need human judgment until an artifact family
  produces enough examples to justify tighter heuristics.

## Downstream Plan

Next phase focus:

1. P6.1: define the integrated feature constraint graph showcase brief.
2. P6.2: promote or generate the showcase fixture evidence.
3. P6.3: produce the showcase figure through the repo-native figure pipeline.
4. P6.4: decide whether Figma MCP adds enough value after seeing the showcase
   artifact and the P5 visual-integrity gates together.

## Phase-Close Acceptance

P5 close is accepted because:

- all planned P5 gates are implemented and in the default quality-gate path;
- forced failure fixtures exist for token drift, text overflow, overlap,
  contrast, missing screenshots, dimension mismatch, and hash mismatch;
- the first screenshot baseline exists as a committed manifest entry;
- downstream P6 work now has a measurable visual-integrity contract.
