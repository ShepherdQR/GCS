# UI Design System Execution Plan

Snapshot date: 2026-05-24.

This is the execution plan for bringing the GCS UI design system from named
conventions into implemented, QA-checked product and figure workflows.

Governing conventions:

- **GCS Quiet Technical Atelier**
- **GCS Warm Evidence Tokens**
- **GCS Evidence-First Interface Grammar**
- **GCS Scientific Figure Pipeline**
- **GCS Visual Integrity Gate**
- **GCS Art Director Review**

## Execution Protocol

Every step in this plan follows the same loop:

1. Do the smallest coherent implementation or documentation change.
2. Summarize what changed and what evidence was produced.
3. Update the remaining steps in the current phase if the work changed what
   should happen next.
4. Run the relevant checks.
5. Commit only the files for that step.
6. Start the next step.

Every phase follows a larger loop:

1. Confirm all phase steps are done or intentionally deferred.
2. Reassess the later phases against the current repo state.
3. Update this plan before starting the next phase.
4. Commit the phase-close planning update.

Do not batch unrelated UI-design-system work into one commit merely because it
is nearby. If a step touches implementation, generated artifacts, and docs, the
commit message must name the step's purpose.

## Phase Status

| Phase | Name | Status | Purpose |
| --- | --- | --- | --- |
| P0 | Convention Foundation | In progress | Name the UI design system and make it governable. |
| P1 | Governance And Agents | Done | Give future work dedicated skills, agents, and review responsibilities. |
| P2 | Token Unification | Done | Make GUI, figures, and reports consume the same semantic token vocabulary. |
| P3 | Viewer UI Implementation | Done | Apply the design system to the Python viewer without moving solver truth into UI. |
| P4 | Scientific Figure Pipeline | Done | Replace coordinate-heavy dense figures with spec-driven, layout-aware production. |
| P5 | Visual Integrity QA | Done | Add screenshot, contrast, overflow, and overlap checks as repeatable gates. |
| P6 | Showcase And Editorial Polish | In progress | Produce a top-tier integrated showcase and decide whether to add Figma MCP. |

## P0: Convention Foundation

Goal: ensure the project has named, durable UI design conventions.

| Step | Status | Output | Checks |
| --- | --- | --- | --- |
| P0.1 | Done | `75-ui-design-system-conventions.md` names the UI design system conventions. | `git diff --check` |
| P0.2 | Pending | Align `72-ui-aesthetic-roadmap.md`, `73-gcs-visual-taste-guide.md`, and `74-scientific-figure-production-paradigm.md` with the convention names. | Markdown diff check |
| P0.3 | Pending | Add a short design-system index under `docs/architecture/70-visualization/` or keep `75` as the single entry after review. | Architecture README check |

P0.1 completion summary:

- Established the canonical convention names.
- Added a design-system acceptance rule: every UI or figure change should name
  its governing convention.
- Committed as `e01da51 docs: name gcs ui design conventions`.

Updated P0 next steps:

- P0.2 should now focus on cross-linking existing aesthetic docs to `75`.
- P0.3 should decide whether a separate visualization index is necessary or
  whether `README.md` plus `75` is enough.

## P1: Governance And Agents

Goal: give the design system persistent working roles.

| Step | Status | Output | Checks |
| --- | --- | --- | --- |
| P1.1 | Done | `gcs-ui-design-steward` skill or role card for UI convention enforcement. | Skill/frontmatter validation by inspection |
| P1.2 | Done | `gcs-figure-art-director` agent role for independent visual review. | Role card references `75`, `73`, `74` |
| P1.3 | Done | Update existing `gcs-scientific-figure-producer` skill to cite `75` as the design-system entry. | `git diff --check` |
| P1.4 | Done | Add a step-template snippet for "summary, update steps, commit, continue." | Template references this plan |

Phase-close replanning requirement:

- Decide whether the UI steward remains a skill, an agent role, or both.
- Decide whether art-director review is required for all UI changes or only
  dense figures and showcase surfaces.

P1 partial completion summary:

- Added `.codex/skills/gcs-ui-design-steward/SKILL.md`.
- Added `Atelier Steward: Calibrate-Review` as the convention-enforcement
  institutional agent.
- Added `Art Director: Frame-Judge` as the independent visual-review
  institutional agent.
- Updated `gcs-scientific-figure-producer` to treat `75` as its design-system
  entry point and to update this plan when figure work changes the roadmap.

Updated P1 next steps:

- P1.1 is satisfied by the new skill and steward role card.
- P1.2 is satisfied by the art-director role card.
- P1.3 is satisfied by the scientific figure producer skill update.
- P1.4 is satisfied by the PBCA step loop in
  `docs/agentic/execution-plan-template.md`.

P1.4 completion summary:

- Added a PBCA step loop to `docs/agentic/execution-plan-template.md`.
- Defined Plan, Build, Check, and Act actions for every step in a multi-step
  execution plan.
- Added a reusable step completion note with changed files, evidence,
  follow-up adjustment, and commit fields.

P1 phase-close replanning:

- P1 is complete enough to support future UI design-system work.
- P2 remains the next implementation phase, but P0.2 and P0.3 are still useful
  documentation cleanup steps and can be handled opportunistically before or
  during P2.
- P2 should begin with a token inventory rather than token generation, because
  the UI and figure surfaces now have named conventions and stewardship roles.

## P2: Token Unification

Goal: make `GCS Warm Evidence Tokens` executable across figures and the viewer.

| Step | Status | Output | Checks |
| --- | --- | --- | --- |
| P2.1 | Done | `78-ui-token-inventory.md` inventories current GUI colors, figure tokens, Matplotlib styles, state colors, renderer fallbacks, and terminal/Rich styles. | Inventory doc |
| P2.2 | Done | `79-ui-token-taxonomy.md` defines canonical token names and cross-surface mappings for surface, text, rule, evidence, state, geometry, constraint, rigid-set, figure, and viewer roles. | Token table diff |
| P2.3 | Done | `python/gcs_viz/color_scheme.py` mirrors canonical tokens and preserves compatibility aliases for viewer code. | Python syntax check |
| P2.4 | Done | `figure71_html_compositor.py` emits canonical `--gcs-*` CSS token aliases and `70-visualization/figure-renderer-token-usage.md` documents renderer token use. | Figure QA smoke |

Phase-close replanning requirement:

- Reassess whether tokens should remain JSON/Python mirrors or move to one
  generated source.

P2.1 completion summary:

- Added `78-ui-token-inventory.md` as the current token-source inventory for
  viewer, Matplotlib, Tkinter/ttk, figure renderers, HTML composition, and
  terminal/Rich surfaces.
- Identified the main unification gap: figure tokens are evidence-semantic
  while Python viewer tokens are UI-role oriented.
- Identified duplicate renderer fallback dictionaries, Python-only rigid-set
  palettes, and an older terminal style as migration targets.

Updated P2 next steps:

- P2.2 should define the canonical token taxonomy and mapping table before
  any runtime code changes.
- P2.3 should mirror the chosen vocabulary into
  `python/gcs_viz/color_scheme.py` while preserving viewer behavior and solver
  boundaries.
- P2.4 should align the HTML/CSS compositor and document renderer token use
  after the Python mirror exists.

P2.2 completion summary:

- Added `79-ui-token-taxonomy.md` as the canonical `GCS Warm Evidence Tokens`
  naming and mapping table.
- Defined lowercase dot-path token names for surface, text, rule, evidence,
  state, geometry, constraint, rigid-set, figure, and viewer style roles.
- Recorded alias rules for the Python viewer mirror in P2.3 and CSS/HTML
  compositor alignment in P2.4.

Updated P2 next steps:

- P2.3 should add a canonical token layer to
  `python/gcs_viz/color_scheme.py`, then keep existing `GCS_THEME`,
  `RIGID_SET_COLORS`, and `CONSTRAINT_COLORS` as compatibility aliases.
- P2.3 may move viewer marker and line-style tokens only if it can do so
  without changing renderer behavior.
- P2.4 should consume the canonical names from the figure compositor side after
  the Python mirror has landed.

P2.3 completion summary:

- Added `GCS_TOKENS` to `python/gcs_viz/color_scheme.py` using the canonical
  token names from `79-ui-token-taxonomy.md`.
- Preserved `GCS_THEME`, `RIGID_SET_COLORS`, and `CONSTRAINT_COLORS` as
  compatibility aliases for existing GUI and renderer code.
- Moved geometry marker, geometry node-size, constraint line-style, and
  graph-line-style tokens into `color_scheme.py`; `visualizer.py` now imports
  those aliases instead of defining local duplicates.

Updated P2 next steps:

- P2.4 should align `figure71_html_compositor.py` with canonical token names
  and document CSS custom-property naming for future figure renderers.
- P2 phase close should decide whether the token source should remain mirrored
  JSON/Python or move to generated artifacts.

P2.4 completion summary:

- Updated `figure71_html_compositor.py` to canonicalize theme colors into
  dot-path token aliases while preserving existing short figure token keys.
- Emitted canonical `--gcs-*` CSS custom properties and kept older CSS aliases
  as transition shims.
- Added `docs/architecture/70-visualization/figure-renderer-token-usage.md` to
  define CSS custom-property naming and renderer token rules.

Updated P2 phase-close work:

- P2 can now close after a short source-of-truth decision: keep JSON/Python
  mirrors for now, or add generation from one token artifact.
- P3 should treat `python/gcs_viz/color_scheme.py` as the viewer mirror and
  avoid new raw hex values in GUI or Matplotlib renderer code.

P2 phase-close summary:

- Closed P2 after landing inventory, taxonomy, Python viewer mirror, and
  HTML/CSS figure renderer token alignment.
- Source-of-truth decision: keep `figure1.theme.json` and
  `python/gcs_viz/color_scheme.py` as mirrored token surfaces for now. Do not
  add token generation until P5 has raw-hex, contrast, and screenshot gates
  stable enough to catch generator mistakes.
- P3 starts from the rule that viewer code should consume `GCS_TOKENS`,
  `GCS_THEME`, or exported compatibility palettes, not fresh hex values.
- P4 starts from the rule that figure specs may keep short evidence keys only
  at the compatibility boundary; renderer internals should prefer canonical
  dot-path tokens and `--gcs-*` CSS variables.

Post-P2 replanning:

- P3 is now the next implementation phase and should begin with a raw-token
  audit before layout changes.
- P4 can build on `figure-renderer-token-usage.md` and the compositor's
  canonical CSS variables.
- P5 should add token linting before deeper screenshot and overlap gates.
- P6 should delay any Figma MCP decision until repo-native token and QA gates
  are reliable.

## P3: Viewer UI Implementation

Goal: apply the design system to the actual local viewer while preserving
solver/runtime/viewer boundaries.

| Step | Status | Output | Checks |
| --- | --- | --- | --- |
| P3.1 | Done | `70-visualization/viewer-token-audit.md` records the raw-token audit and `platform.py` now uses `GCS_THEME` for legacy textual DOF/status styles. | Raw-token audit plus Python syntax check |
| P3.2 | Done | `STATE_COLORS` exposes canonical state aliases and viewer state/focus consumers now use those aliases without changing command ownership. | AST syntax checks and state-token audit |
| P3.3 | Done | `70-visualization/viewer-inspector-layout-audit.md` confirms the active inspector layout and marks the old stacked left panel as legacy-unused. | Inspector audit plus AST syntax check |
| P3.4 | Done | `70-visualization/viewer-replay-solve-polish.md` records replay/solve rail state-color and message-tone polish. | AST syntax and focused diff checks |

Phase-close replanning requirement:

- Compare implementation with `72-ui-aesthetic-roadmap.md`.
- Decide whether GUI work needs a dedicated screenshot baseline suite before
  further feature polish.

P3.1 completion summary:

- Added `docs/architecture/70-visualization/viewer-token-audit.md`.
- Confirmed that `color_scheme.py` is the intentional Python raw-hex source,
  while `visualizer.py` and `platform_gui.py` consume token aliases.
- Replaced legacy textual DOF and status Rich styles in `platform.py` with
  `GCS_THEME` aliases, removing the old dark status color.

Updated P3 next steps:

- P3.2 should focus on canonical state aliases for selected, replay-current,
  violated, solved, warning, and error surfaces.
- P3.3 and P3.4 should avoid layout or evidence changes that add raw hex
  values outside `color_scheme.py`.

P3.2 completion summary:

- Added `STATE_COLORS` in `python/gcs_viz/color_scheme.py` for focus,
  focus-active, selected, replay-current, solved, info, warning, error,
  pending, and violated states.
- Updated `platform_gui.py`, `platform.py`, and `visualizer.py` so status,
  DOF, button focus, selected geometry, focused constraints, and graph halos
  use canonical state aliases.
- Preserved compatibility `GCS_THEME` aliases for older call sites and avoided
  command, solver, runtime, and scene-state changes.

Updated P3 next steps:

- P3.3 can reshape inspector layout using existing token and state aliases.
- P3.4 should reuse `STATE_COLORS["replay_current"]` for replay-current
  evidence and `STATE_COLORS["violated"]` for constraint violation surfaces.

P3.3 completion summary:

- Added `docs/architecture/70-visualization/viewer-inspector-layout-audit.md`.
- Confirmed that the active Tk inspector already has the required model
  summary, tabbed object browser, local object controls, and command zone.
- Renamed the unused old `_build_left_panel` path to
  `_build_left_panel_legacy_unused` and marked it as legacy comparison code so
  future work does not accidentally revive the stacked debug layout.

Updated P3 next steps:

- P3.4 should polish replay and solve evidence around the viewport and status
  rail, not start another left-inspector rewrite.

P3.4 completion summary:

- Added `docs/architecture/70-visualization/viewer-replay-solve-polish.md`.
- Kept replay and solve rails as transient GUI evidence surfaces and colored
  their state labels through `STATE_COLORS`.
- Standardized solve/replay messages around `Solving`, `Solved`,
  `Solve warning`, `Replay step`, and `Replay complete`.

Updated P3 phase-close work:

- P3 can close after a short review against `72-ui-aesthetic-roadmap.md`.
- P4 should now proceed on the figure pipeline; P5 should later add screenshot
  baselines for the viewer rail states touched here.

P3 phase-close summary:

- Closed P3 after viewer token audit, canonical state aliases, inspector layout
  audit, and replay/solve rail polish.
- The active Tk viewer now has a token-governed model inspector, state-colored
  transient replay/solve evidence, and no known raw hex values outside
  `color_scheme.py`.
- Solver/runtime/viewer ownership boundaries stayed intact: no solver command,
  scene schema, history persistence, or renderer mutation ownership changes
  were introduced.
- Validation remained lightweight because this environment lacks the full GUI
  dependency/display path; P5 should add screenshot baselines for visual proof.

Post-P3 replanning:

- P4.1 should upgrade execution-map specs so canonical token fields are present
  in specs before regenerating assets.
- P4.2 should add browser export only after the schema can drive canonical
  `--gcs-*` token output consistently.
- P5.1 should encode the P3 raw-hex rule as an automated lint before broader
  screenshot and overlap gates.
- P6 should remain blocked on a stable figure pipeline and visual integrity
  gates; external Figma MCP remains a later governance decision.

## P4: Scientific Figure Pipeline

Goal: move dense figures from prototype SVG drawing to `GCS Scientific Figure
Pipeline`.

| Step | Status | Output | Checks |
| --- | --- | --- | --- |
| P4.1 | Done | `execution-map-spec-schema.md`, `figure71.yaml`, compositor support, and `figure_qa.py` establish `gcs.execution_map.v1` with canonical token fields. | Spec QA |
| P4.2 | Done | `browser_export.py`, Figure 71 browser manifest, and review PNG/PDF artifacts add a thin browser-rendered export smoke. | Browser smoke plus figure QA |
| P4.3 | Done | `84-p4-3-graph-chart-backend-decision.md` defers graph/chart panel backends for P4.4. | Dependency decision |
| P4.4 | Done | Rebuilt Figure 71 from the repo-native pipeline and demoted old SVG output to historical prototype. | `figure_qa.py` plus review artifact |

Phase-close replanning requirement:

- Decide whether Figma MCP is needed for showcase polish after repo-native
  browser QA is stable.

P4.1 completion summary:

- Added `docs/architecture/70-visualization/execution-map-spec-schema.md`.
- Upgraded `tools/architecture_visualization/specs/figure71.yaml` to
  `gcs.execution_map.v1` with `expected_step_range`, `token_taxonomy`, and
  per-arc `canonical_token` fields.
- Updated `figure71_html_compositor.py` to prefer `canonical_token` while
  preserving short-token compatibility.
- Updated `figure_qa.py` to check schema version and canonical evidence-token
  coverage.

Updated P4 next steps:

- P4.2 can now add browser export on top of a schema that already carries
  canonical token fields.
- P4.3 should defer chart/graph backends until dependency governance approves
  any new renderer packages.
- P4.4 should rebuild generated assets only after P4.2 export behavior is
  stable.

P4.2 completion summary:

- Added `tools/architecture_visualization/browser_export.py` as a
  dependency-light Chromium CLI export smoke for tokenized HTML figures.
- Extended `figure71.yaml` with browser manifest and review PNG/PDF exports.
- Regenerated the Figure 71 HTML, PNG, PDF, manifest, and QA JSON through the
  browser export path.
- Updated `figure_qa.py` so `quality.browser_smoke_required` checks the
  manifest, export status, token proof, and exported artifact existence.

Updated P4 next steps:

- P5.1 should run next, before P4.4, so raw-hex and unknown-token linting guard
  the rebuilt artifacts.
- P4.3 remains a dependency-governance decision and should stay small unless a
  new graph/chart backend becomes necessary.
- P4.4 should rebuild and demote historical SVG output only after P5.1 is in
  place.

P4.3 completion summary:

- Added `docs/architecture/84-p4-3-graph-chart-backend-decision.md`.
- Recorded `ThirdPartyDecision`: defer external graph/chart backends for P4.4.
- Preserved repo-native Figure 71 production through semantic spec,
  `figure1.theme.json`, HTML/CSS compositor, browser export smoke, figure QA,
  and token lint.
- Recorded future provider order and dependency metadata requirements for any
  later Graphviz/D2/ELK/Vega-style request.

Updated P4 next steps after P4.3:

- P4.4 should now rebuild Figure 71 assets without adding new dependencies.
- P4 phase close should evaluate repo-native pipeline stability after P4.4,
  before P5.2/P5.3 and before any Figma MCP decision.

P4.4 completion summary:

- Rebuilt the Figure 71 display path around the browser-rendered review PNG,
  editable HTML, review PDF, browser manifest, and structural QA artifact.
- Updated `71-step-1-40-execution-report.md` so the Procedure Figure embeds
  the review PNG and keeps the old coordinate-drawn SVG only as historical
  prototype.
- Added `--reuse-existing-artifacts` to `browser_export.py` and unit coverage
  for manifest refresh when browser artifacts exist but browser CLI shutdown is
  unreliable.
- Added `85-p4-4-execution-map-rebuild.md` with rebuild evidence and follow-up.

Updated P4 phase-close work:

- P4 can now close with a phase summary and downstream plan update.
- P5.2 should begin after P4 close and focus on rendered text overflow.

P4 phase-close summary:

- Added `86-p4-scientific-figure-pipeline-phase-close.md`.
- Closed P4 after completing schema stabilization, browser export smoke,
  graph/chart backend governance, and Figure 71 rebuild/prototype demotion.
- Recorded stable decisions: specs are source of truth, repo-native pipeline
  remains sufficient for Figure 71, graph/chart dependencies are deferred, and
  Figma MCP remains a later P6.4 decision.
- Moved active downstream work to P5.2 rendered text overflow checks.

Current next-work plan:

- `82-ui-design-next-work-plan.md` persists the P4.2-through-P6 sequence and
  records the preferred operating bias: keep P4.2 thin, add P5.1 token lint
  before P4.4 asset rebuild, and delay Figma MCP until repo-native QA is
  reliable.

## P5: Visual Integrity QA

Goal: make `GCS Visual Integrity Gate` measurable.

| Step | Status | Output | Checks |
| --- | --- | --- | --- |
| P5.1 | Done | `gcs_token_lint.py` enforces raw-hex and unknown-token linting for GUI, Matplotlib, and figure renderer code. | Forced raw-hex fixture fails |
| P5.2 | Done | `gcs_text_overflow.py` checks Figure 71 HTML text budgets and forced overflow fixtures. | QA fixture fails on forced overflow |
| P5.3 | Done | `gcs_overlap_contrast.py` checks Figure 71 layout boxes and contrast targets. | Forced overlap plus contrast report |
| P5.4 | Done | `gcs_screenshot_baseline.py` checks the first screenshot-baseline manifest and Figure 71 review PNG digest. | Stable baseline policy |

Phase-close replanning requirement:

- Decide which visual gates are required in default quality gates and which are
  reviewer-only.

P5.1 completion summary:

- Added `tools/ui_qa/gcs_token_lint.py` as a standard-library lint for raw
  `#RRGGBB` values outside approved token sources, unknown Python token
  dictionary references, and unknown figure-spec `canonical_token` values.
- Replaced renderer-local raw hex fallback dictionaries with loading from
  `tools/architecture_visualization/figure1.theme.json`.
- Added `tests/tools/test_gcs_token_lint.py` with passing-current-repo and
  forced-failure fixtures, then promoted the lint and test into the default
  agentic quality-gate sequence.
- Added `docs/architecture/70-visualization/token-lint-gate.md` as the durable
  P5.1 rule.

Updated P5 next steps:

- P4.3 should record the graph/chart backend dependency decision before any
  new renderer package is introduced.
- P4.4 can now rebuild Figure 71 with token drift guarded automatically.
- P5.2 should focus on rendered text overflow rather than expanding token
  lint into a broader layout checker.

P5.2 completion summary:

- Added `tools/ui_qa/gcs_text_overflow.py` as a standard-library text-budget
  checker for generated HTML figures.
- Added text-budget markers to Figure 71 title, subtitle, procedure claim,
  panel titles, token chips, panel claims, step focus labels, and step evidence
  text.
- Added `tests/tools/test_gcs_text_overflow.py` with current Figure 71 pass,
  forced overflow failure, and missing-budget failure.
- Promoted `python.gcs_text_overflow` and
  `python.gcs_text_overflow_tests` into default quality gates.
- Added `docs/architecture/70-visualization/text-overflow-gate.md`.

Updated P5 next steps after P5.2:

- P5.3 should add overlap and contrast gates over the same figure/HTML
  artifact family.
- P5.4 should decide screenshot baselines after the source-level gates are in
  place.

P5.3 completion summary:

- Added `tools/ui_qa/gcs_overlap_contrast.py` as a standard-library
  source-level overlap and contrast checker.
- Added six Figure 71 panel layout boxes and 21 contrast targets to the HTML
  compositor output.
- Added `tests/tools/test_gcs_overlap_contrast.py` with current Figure 71 pass,
  forced overlap failure, forced weak-contrast failure, and missing-marker
  failure.
- Promoted `python.gcs_overlap_contrast` and
  `python.gcs_overlap_contrast_tests` into default quality gates.
- Added `docs/architecture/70-visualization/overlap-contrast-gate.md`.

Updated P5 next steps after P5.3:

- P5.4 should now add screenshot baselines over the same Figure 71 and viewer
  states.
- P6 showcase work should wait until P5.4 records baseline policy.

P5.4 completion summary:

- Added `docs/architecture/70-visualization/assets/screenshot-baselines.json`
  with the Figure 71 browser-rendered review PNG as the first stable baseline.
- Added `tools/ui_qa/gcs_screenshot_baseline.py` as a standard-library checker
  for PNG signature, dimensions, byte count, minimum byte count, and SHA256.
- Added `tests/tools/test_gcs_screenshot_baseline.py` with current-manifest
  pass, missing-file failure, dimension-mismatch failure, and hash-mismatch
  failure.
- Promoted `python.gcs_screenshot_baseline` and
  `python.gcs_screenshot_baseline_tests` into default quality gates.
- Added `docs/architecture/70-visualization/screenshot-baseline-gate.md`.

Updated P5 next steps after P5.4:

- Close P5 by deciding which visual-integrity gates are default quality gates
  and which remain reviewer-only.
- P6.1 showcase brief should start only after the phase-close decision records
  how showcase artifacts will be judged.

P5 phase-close summary:

- Added `docs/architecture/87-p5-visual-integrity-phase-close.md`.
- Closed P5 after token lint, text overflow, overlap/contrast, and screenshot
  baseline gates entered the default quality-gate sequence.
- Recorded that deterministic source/artifact checks are default gates, while
  main-claim clarity, editorial hierarchy, and design-tool value remain
  reviewer-only `GCS Art Director Review` decisions.
- Moved the active downstream phase to P6 showcase and editorial polish.

Updated P6 next steps after P5 close:

- P6.1 should define the showcase brief before changing fixture or figure
  assets.
- P6.4 should judge Figma MCP only after P6.3 produces a repo-native showcase
  artifact that exposes the remaining collaboration gap.

## P6: Showcase And Editorial Polish

Goal: produce a top-tier showcase of GCS local-to-global solving and decide on
external design-surface integration.

| Step | Status | Output | Checks |
| --- | --- | --- | --- |
| P6.1 | Done | `88-p6-1-integrated-showcase-brief.md` defines the showcase claim, evidence vocabulary, panels, and review questions. | Brief review |
| P6.2 | Next | Generate or promote showcase fixture with expected rank, gluing, replay, and diagnostic evidence. | Public gate |
| P6.3 | Pending | Produce showcase figure through the scientific figure pipeline and tokenized HTML compositor. | Visual integrity QA |
| P6.4 | Pending | Decide whether to install/configure Figma MCP only after repo-native token and QA gates are reliable. | Governance decision |

Phase-close replanning requirement:

- Decide the next aesthetic target: product UI refinement, paper figure, demo
  deck, or external design-tool integration.

P6.1 completion summary:

- Added `docs/architecture/88-p6-1-integrated-showcase-brief.md`.
- Defined the five-second claim: one public constraint scene carries solve
  intent through decomposition, numeric rank/residual evidence, gluing
  diagnostics, viewer projection, CLI smoke, and negative rejection evidence.
- Named source evidence, canonical tokens, required panels, production
  direction, and Art Director review questions.
- Kept fixture and figure assets unchanged so P6.2 can promote evidence before
  P6.3 changes visuals.

Updated P6 next steps after P6.1:

- P6.2 should promote or enrich fixture evidence in renderer-consumable form.
- P6.3 should produce the showcase figure against the P6.1 brief and P5
  visual-integrity gates.
- P6.4 should judge Figma MCP against the actual P6.3 artifact and remaining
  collaboration gap.
