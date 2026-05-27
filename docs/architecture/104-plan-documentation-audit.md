# Plan Documentation Audit — Complete Map

Date: 2026-05-28
Status: active

## Purpose

Verify that every plan, design decision, and development item across all
narrative lines has a corresponding persisted document. This is the index of
indexes — a single place to check whether a given plan exists on disk.

---

## 1. Strategic Layer

| Document | Status | Covers |
| --- | --- | --- |
| `docs/architecture/95-gcs-narrative-map.md` | Active | 14 narrative lines, 4 arcs, development levels, v2 evidence routes, promotion gates, execution phases, decision rules, next task queue |
| `docs/architecture/98-narrative-line-capability-demonstrations.md` | Active | Tangible evidence per narrative line: commands to run, outputs to inspect, the 5-Minute Trust Test, the Evidence Chain Test |
| `docs/architecture/99-weak-line-development-plan.md` | Active | Short/medium/long-term plans for weak lines, dependency graph, review rhythm |

---

## 2. Weak-Line Development Plans

### Short-Term (S1–S5) — All Complete

| ID | Item | Design doc | Deliverable |
| --- | --- | --- | --- |
| S1 | E-GOV-001 validator | `99-weak-line-development-plan.md` §S1 | `tools/agentic_design/e_gov_001_staging_validator.py` |
| S2 | D6 evidence walkthrough | `99` §S2 | `docs/product/demos/d6-evidence-walkthrough/README.md` |
| S3 | R2 build transcript | `99` §S3 | `docs/product/build-transcripts/r2-build-transcript-20260527.md` |
| S4 | Quality gate trend | `99` §S4 | `docs/agentic/metrics-dashboard.md` (trend section) |
| S5 | I001 agent promotion | `99` §S5 | `docs/agentic/institutional-agents/001-bladesmith-quench-forge/promotion-20260527.md` |

### Medium-Term (M1–M5) — Designed, Not Executed

| ID | Item | Design doc | Implementation doc |
| --- | --- | --- | --- |
| M1 | External baseline run | `100-medium-term-design.md` §M1 | Not yet started |
| M2 | Researcher review packet | `100` §M2 | Not yet started |
| M3 | Fixture corpus ladder | `100` §M3 | Not yet started |
| M4 | Replay checker in gate | `100` §M4 | Not yet started |
| M5 | B2 expected-output files | `100` §M5 | Not yet started |

**Design doc:** `docs/architecture/100-medium-term-design.md` — detailed design
with file paths, technical approach, and verification commands for all M1–M5.

### Long-Term (L1–L5) — Designed, Dependencies Not Met

| ID | Item | Design doc | Blocked by |
| --- | --- | --- | --- |
| L1 | External review archive | `101-long-term-design.md` §L1 | M2 |
| L2 | Second agent promotion | `101` §L2 | S5 + accumulated usage |
| L3 | Public release snapshot | `101` §L3 | M1, M4 |
| L4 | Contribution workflow | `101` §L4 | L1 |
| L5 | Multi-dimension trends | `101` §L5 | S4 + 10 task closures |

**Design doc:** `docs/architecture/101-long-term-design.md` — parametric design
with templates, acceptance criteria, and dependency resolution strategies.

---

## 3. Aesthetic Development Plans

### Immediate (A1–A2) — Complete

| ID | Item | Design doc | Deliverable |
| --- | --- | --- | --- |
| A1 | Bridge taste seed | `103-short-term-aesthetic-plan.md` §A1 | `docs/research/20260527/aesthetic-taste/bridge_constraint_graph.png` |
| A2 | Full-window screenshot | `103` §A2 | `docs/architecture/70-visualization/assets/ve003-full-window-viewer-20260528.png` + `tools/ui_qa/capture_full_window.py` |

### Short-Term (A3–A4) — Designed, Not Executed

| ID | Item | Design doc |
| --- | --- | --- |
| A3 | Color palette temperature audit | `103-short-term-aesthetic-plan.md` §A3 |
| A4 | Contrast ratio verification | `103` §A4 |

### Medium-Term (A5–A6) — Designed in UI Aesthetic Roadmap

| ID | Item | Design doc |
| --- | --- | --- |
| A5 | Phase 3: Inspector Layout | `docs/architecture/72-ui-aesthetic-phase-3-inspector-layout.md` |
| A6 | Phase 4: Replay Polish | `docs/architecture/72-ui-aesthetic-phase-4-replay-solve-polish.md` |

### Long-Term (A7–A8) — Described in Re-Evaluation, Dedicated Doc Below

| ID | Item | Design doc |
| --- | --- | --- |
| A7 | Visual identity brief | `docs/architecture/102-aesthetic-taste-reevaluation.md` §A7; detailed in `105-long-term-aesthetic-design.md` |
| A8 | Figure gallery | `docs/architecture/102-aesthetic-taste-reevaluation.md` §A8; detailed in `105-long-term-aesthetic-design.md` |

---

## 4. Narrative Map Next-Task Queue Coverage

| # | Task (from 95-gcs-narrative-map.md) | Covered by | Status |
| --- | --- | --- | --- |
| 1 | R2 reproducible build transcript | S3 | Done |
| 2 | E-GOV-001 validator candidate | S1 | Done |
| 3 | B2 expected-output files | M5 | Designed, not executed |
| 4 | External adapter path | M1 | Designed, not executed |
| 5 | D5 workbench / D6 walkthrough | S2 | Done |
| 6 | External researcher review archive | M2 → L1 | Designed, blocked on external |
| 7 | Contribution workflow example | L4 | Designed, blocked on L1 |

All 7 narrative-map next tasks have coverage in a design document.

---

## 5. Supporting Documents (Existing)

| Document | Purpose | Status |
| --- | --- | --- |
| `docs/architecture/72-ui-aesthetic-roadmap.md` | UI aesthetic thesis, 5 phases | Active |
| `docs/architecture/72-ui-aesthetic-phase-1-theme-foundation.md` | Color tokens, theme | Active |
| `docs/architecture/72-ui-aesthetic-phase-2-viewport-semantics.md` | Viewport encoding | Active |
| `docs/architecture/72-ui-aesthetic-phase-3-inspector-layout.md` | Tabbed inspector | Active (not implemented) |
| `docs/architecture/72-ui-aesthetic-phase-4-replay-solve-polish.md` | Replay rail | Active (not implemented) |
| `docs/architecture/72-ui-aesthetic-phase-5-design-qa-accessibility.md` | QA gates | Active |
| `docs/architecture/77-ui-design-development-plan-report.md` | Phases 6–10 | Active |
| `docs/architecture/96-fixture-corpus-maturity-ladder.md` | C0–C4 ladder | Exists (content TBD per M3) |
| `docs/architecture/97-external-solver-comparison-and-benchmark-plan.md` | Comparison plan | Exists |
| `docs/architecture/97-ui-viewer-figure-integration-plan.md` | Viewer/figure integration | Exists |
| `docs/architecture/98-benchmark-candidate-selection-criteria.md` | B2 criteria | Exists |
| `docs/architecture/98-ui-viewer-figure-development-plan.md` | UI dev plan | Exists |
| `docs/product/gcs-product-user-brief.md` | Product brief | Exists |
| `docs/product/gcs-demo-ladder.md` | D0–D5 demo ladder | Exists |
| `docs/product/20-minute-contributor-path.md` | Onboarding | Exists |
| `docs/product/release-readiness-checklist.md` | Release checklist | Exists |
| `docs/product/researcher-audience-strategy.md` | Audience strategy | Exists |
| `docs/product/researcher-contribution-boundary.md` | Contribution boundary | Exists |
| `docs/agentic/metrics-dashboard.md` | Metrics + trend history | Active |
| `docs/agentic/institutional-agent-registry-and-scorecard.md` | Agent registry | Active |
| `docs/agentic/evals/governance/exercised-evidence-20260526.md` | Governance evidence | Active |

---

## 6. Gaps Found

### Gap 1: A7/A8 Long-Term Aesthetic Design (FIXED)

A7 (visual identity brief) and A8 (figure gallery) were described in
`102-aesthetic-taste-reevaluation.md` at ~3 lines each — enough for a
re-evaluation but not enough for implementation. A dedicated design doc
has been created at `docs/architecture/105-long-term-aesthetic-design.md`.

### Gap 2: Untracked Redundant Document

`docs/architecture/99-narrative-weakness-analysis-20260527.md` exists on disk
but is not tracked in git. Its content overlaps significantly with:
- `docs/architecture/99-weak-line-development-plan.md`
- `docs/architecture/98-narrative-line-capability-demonstrations.md`

Recommendation: delete the untracked file. If any unique content needs
preservation, merge it into one of the tracked documents.

### Gap 3: Numbering Collisions (Pre-Existing)

Multiple documents share the same numeric prefix (95, 97, 98, 99). This is a
pre-existing condition from documents created across sessions. The narrative
map uses descriptive slugs rather than numbers, so the collisions are cosmetic
but confusing. Not addressed in this audit — requires a separate numbering
cleanup pass.

### Non-Gap: Contribution Workflow

`docs/product/contribution-workflow.md` does not exist. This is correct — it
is an L4 deliverable that depends on L1 (external review/contribution). The
design is in `101-long-term-design.md` §L4 with a full template.

---

## 7. Complete Document Index

All plan/design documents in `docs/architecture/` with numeric prefix:

| # | Document | Layer | Status |
| --- | --- | --- | --- |
| 95 | `95-gcs-narrative-map.md` | Strategic | Active |
| 96 | `96-fixture-corpus-maturity-ladder.md` | Solver Evidence | Active (M3 target) |
| 97 | `97-external-solver-comparison-and-benchmark-plan.md` | Product | Active |
| 97 | `97-ui-viewer-figure-integration-plan.md` | Workbench | Active |
| 98 | `98-benchmark-candidate-selection-criteria.md` | Product | Active |
| 98 | `98-ui-viewer-figure-development-plan.md` | Workbench | Active |
| 98 | `98-narrative-line-capability-demonstrations.md` | Strategic | Active |
| 99 | `99-weak-line-development-plan.md` | Strategic | Active |
| 100 | `100-medium-term-design.md` | Tactical | Active |
| 101 | `101-long-term-design.md` | Tactical | Active |
| 102 | `102-aesthetic-taste-reevaluation.md` | Aesthetic | Active |
| 103 | `103-short-term-aesthetic-plan.md` | Aesthetic | Active |
| 104 | `104-plan-documentation-audit.md` | Governance | Active (this doc) |
| 105 | `105-long-term-aesthetic-design.md` | Aesthetic | Active |

---

## 8. Verification

Every plan item from every layer can be traced to a persisted document:

- Narrative map → 95
- Weak line analysis → 98 (demonstrations) + 99 (S/M/L plan)
- Medium-term design → 100
- Long-term design → 101
- Aesthetic re-evaluation → 102
- Short-term aesthetic → 103
- Long-term aesthetic → 105
- UI aesthetic phases → 72-* series
- Product/demo → `docs/product/` series
- Agentic/governance → `docs/agentic/` series

No plan item exists only in conversation context. Every decision has a file.
