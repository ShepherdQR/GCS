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
| P2 | Token Unification | In progress | Make GUI, figures, and reports consume the same semantic token vocabulary. |
| P3 | Viewer UI Implementation | Pending | Apply the design system to the Python viewer without moving solver truth into UI. |
| P4 | Scientific Figure Pipeline | Pending | Replace coordinate-heavy dense figures with spec-driven, layout-aware production. |
| P5 | Visual Integrity QA | Pending | Add screenshot, contrast, overflow, and overlap checks as repeatable gates. |
| P6 | Showcase And Editorial Polish | Pending | Produce a top-tier integrated showcase and decide whether to add Figma MCP. |

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
| P2.3 | Pending | Mirror figure tokens into `python/gcs_viz/color_scheme.py` without changing interaction logic. | Python syntax check |
| P2.4 | Pending | Align CSS/HTML figure compositor token usage and add notes for future renderers. | Figure QA smoke |

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

## P3: Viewer UI Implementation

Goal: apply the design system to the actual local viewer while preserving
solver/runtime/viewer boundaries.

| Step | Status | Output | Checks |
| --- | --- | --- | --- |
| P3.1 | Pending | Apply theme foundation to Tkinter/ttk and Matplotlib surfaces. | `python -B -m py_compile` for touched files |
| P3.2 | Pending | Implement viewport semantics for geometry markers, constraint line styles, and visual states. | UI QA fixture render or manual screenshot |
| P3.3 | Pending | Reshape inspector layout toward model summary plus tabbed object tables. | Narrow-window smoke |
| P3.4 | Pending | Add replay and solve evidence polish. | Replay fixture smoke |

Phase-close replanning requirement:

- Compare implementation with `72-ui-aesthetic-roadmap.md`.
- Decide whether GUI work needs a dedicated screenshot baseline suite before
  further feature polish.

## P4: Scientific Figure Pipeline

Goal: move dense figures from prototype SVG drawing to `GCS Scientific Figure
Pipeline`.

| Step | Status | Output | Checks |
| --- | --- | --- | --- |
| P4.1 | Pending | Upgrade `figure71.yaml` from prototype JSON-compatible YAML into a stable figure-spec schema. | Spec QA |
| P4.2 | Pending | Add browser-rendered export path for HTML to PNG/PDF/SVG where tooling is available. | Browser smoke |
| P4.3 | Pending | Add graph/chart panel backends after third-party governance. | Dependency decision |
| P4.4 | Pending | Rebuild Figure 71 from the new pipeline and demote the old SVG to historical prototype. | `figure_qa.py` plus review artifact |

Phase-close replanning requirement:

- Decide whether Figma MCP is needed for showcase polish after repo-native
  browser QA is stable.

## P5: Visual Integrity QA

Goal: make `GCS Visual Integrity Gate` measurable.

| Step | Status | Output | Checks |
| --- | --- | --- | --- |
| P5.1 | Pending | Add rendered text overflow checks. | QA fixture fails on forced overflow |
| P5.2 | Pending | Add bounding-box overlap checks for text and critical shapes. | QA fixture fails on forced overlap |
| P5.3 | Pending | Add contrast checks for text and status chips. | Contrast report |
| P5.4 | Pending | Add screenshot baselines for core GUI/figure states. | Stable baseline policy |

Phase-close replanning requirement:

- Decide which visual gates are required in default quality gates and which are
  reviewer-only.

## P6: Showcase And Editorial Polish

Goal: produce a top-tier showcase of GCS local-to-global solving and decide on
external design-surface integration.

| Step | Status | Output | Checks |
| --- | --- | --- | --- |
| P6.1 | Pending | Define integrated feature constraint graph showcase brief. | Brief review |
| P6.2 | Pending | Generate or promote showcase fixture with expected rank/diagnostic evidence. | Public gate |
| P6.3 | Pending | Produce showcase figure through the scientific figure pipeline. | Visual integrity QA |
| P6.4 | Pending | Decide whether to install/configure Figma MCP for final editorial review. | Governance decision |

Phase-close replanning requirement:

- Decide the next aesthetic target: product UI refinement, paper figure, demo
  deck, or external design-tool integration.
