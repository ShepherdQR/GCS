# Short-Term Aesthetic Development Plan

Date: 2026-05-28
Status: active
Depends on: `docs/architecture/102-aesthetic-taste-reevaluation.md`

## Context

The aesthetic re-evaluation identified 8 improvement opportunities ranked by
impact-to-effort. The immediate tier (A1–A2, zero code change) and the
short-term tier (A3–A4, code change with existing infrastructure) form a
coherent batch that can be completed in 1–2 sessions.

This document is the short-term counterpart to the medium/long-term aesthetic
improvements that belong to the UI aesthetic roadmap Phases 3–5.

---

## A1. Bridge Taste Seed

**Status:** executing this session
**Effort:** 1 script + 1 image

### Design

Generate a second taste seed image that bridges "pure taste" (the single
curve) and "solver evidence" (the viewer/figure artifacts).

**Scene:** 3 rigid sets, 2 constraints — the minimal geometric constraint graph
that still carries solver meaning.

**Visual mapping (from GCS palette):**

| Element | Token | Color |
| --- | --- | --- |
| Paper | `surface.paper` | #F7F4EC |
| Node A (rigid set 1) | `rigidSet.palette.01` | #587C7A (teal) |
| Node B (rigid set 2) | `rigidSet.palette.02` | #B88746 (ochre) |
| Node C (rigid set 3) | `rigidSet.palette.05` | #C66E4E (rust) |
| Constraint edge 1 (distance) | `constraint.type.distance.color` | #B88746 |
| Constraint edge 2 (coincident) | `constraint.type.coincident.color` | #B8574E |

**Line styles:**
- Distance constraint: solid, as in `constraint.type.distance.lineStyle`
- Coincident constraint: dotted, as in `constraint.type.coincident.lineStyle`

**Composition:** Three nodes in a gentle triangle. Node positions chosen for
asymmetric balance (not equilateral — asymmetry over symmetry per the taste
seed thesis). Constraints drawn as edges between nodes. Node labels small and
muted (`text.muted` #8B867A). Same A4 paper, same margins, same restraint.

**File:** `docs/research/20260527/aesthetic-taste/bridge_constraint_graph.py`
**Output:** `docs/research/20260527/aesthetic-taste/bridge_constraint_graph.png`

---

## A2. Full-Window Viewer Screenshot

**Status:** executing this session
**Effort:** 1 script + 1 image

### Design

Capture the GCS viewer at 1600×900 with a scene loaded, showing the full
window: canvas, inspector panels, status bar, and toolbar.

**Scene:** `fixtures/scene/saved/triangle_003.json` — already used in VE-002
capture, has constraint and geometry data suitable for display.

**Script approach:** Extend the pattern from `capture_viewer_evidence.py`:
1. Instantiate `GCSPlatformGUI`
2. Load triangle_003.json
3. Set window geometry to 1600×900
4. Use `ImageGrab.grab()` or `root.winfo_geometry()` to capture the full
   window area
5. Save to PNG

**Output:** `docs/architecture/70-visualization/assets/ve003-full-window-viewer-20260528.png`

---

## A3. Color Palette Temperature Audit

**Status:** planned, next session
**Effort:** 1 analysis document

### Design

Add 1–2 cool-muted tokens to create deliberate temperature contrast with the
warm palette. Candidates:
- `surface.cool.muted`: desaturated slate (#D8DCE3)
- `state.inactive`: cool gray (#9BA3AF)

Write a brief audit note at `docs/architecture/72-ui-aesthetic-phase-1-theme-foundation.md`
appending a "Temperature Audit" section with the new tokens and rationale.

**No existing tokens are changed.** This is additive.

---

## A4. Contrast Ratio Verification

**Status:** planned, next session
**Effort:** 1 analysis document

### Design

Write a small script or manual audit that computes WCAG contrast ratios for
key token pairs. Document findings in the same theme foundation doc.

**Key pairs to check:**

| Foreground | Background | Expected ratio |
| --- | --- | --- |
| `text.primary` (#181715) | `surface.paper` (#F7F4EC) | ≥ 4.5:1 |
| `text.secondary` (#5F5B53) | `surface.paper` (#F7F4EC) | ≥ 4.5:1 |
| `text.muted` (#8B867A) | `surface.paper` (#F7F4EC) | ≥ 3:1 (large text only) |
| `state.text.focus` (#87412F) | `surface.panel` (#FFFEFA) | ≥ 4.5:1 |
| `state.text.error` (#8F352F) | `surface.panel` (#FFFEFA) | ≥ 4.5:1 |
| `state.text.ok` (#2F684A) | `surface.panel` (#FFFEFA) | ≥ 4.5:1 |

---

## Execution Order

This session: A1 → A2 → commit → push
Next session: A3 → A4 → commit → push

A1 and A2 are independent and can be developed in parallel.
