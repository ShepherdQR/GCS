# GCS Aesthetic Taste — Re-Evaluation

Date: 2026-05-27
Status: active
Reference: `docs/research/20260527/aesthetic-taste/README.md` (taste seed)
Reference: `docs/architecture/72-ui-aesthetic-roadmap.md` (thesis and phases)

## Purpose

The taste seed image ("A Single Curve") defined a zero-reference for the GCS
visual language. This document re-evaluates the project's aesthetic position
against that reference: what holds, what falls short, and where improvement
is possible within the current implementation and roadmap.

---

## 1. Thesis Coherence — Strong

The "Quiet Technical Atelier" thesis is well-articulated and internally
consistent:

- **Warm technical neutrals** over cool blue-gray chrome
- **Color carries semantic weight** — not decoration
- **Muted categorical colors** for rigid sets — avoid saturated rainbows
- **Restraint over accumulation** — every element must earn its pixel

The thesis is stated in `72-ui-aesthetic-roadmap.md` and instantiated in
`color_scheme.py` (100 named tokens). The taste seed image translates the
thesis into a single visual artifact: one curve, warm paper, no decoration.

**Verdict:** The thesis is clear and defensible. The risk is not incoherence —
it's that the thesis is more legible in documents than in the running
application.

---

## 2. Color Palette Quality — Strong, With Gaps

### What works

The `color_scheme.py` palette is the strongest aesthetic asset:

| Strength | Evidence |
| --- | --- |
| Warm paper hierarchy | `surface.paper` (#F7F4EC) → `surface.canvas` (#FBFAF5) → `surface.panel` (#FFFEFA) — three warm off-whites with distinct roles |
| Muted rigid-set colors | 15 colors, all desaturated — teal (#587C7A), ochre (#B88746), mauve (#7C617B), olive (#788C5D) — no pure RGB/CMY |
| Semantic state colors | Focus (warm rust #C8643F), ok (muted green #4B8A64), warning (amber #B88746), error (earth red #B8574E) — warm-toned, not neon |
| Evidence domain colors | Six evidence categories with distinct fill/stroke pairs, e.g., domain (blue-gray), graph (purple-gray), planner (sage), numeric (olive), diagnostic (amber), failure (rose) |
| Constraint type encoding | Line style (solid, dashed, dotted, dashdot, (3,2)) carries type; color carries emphasis — good separation of concerns |
| Typography | Sans for UI, serif for figures — conventional but appropriate |

### What could improve

| Gap | Current state | Improvement |
| --- | --- | --- |
| Palette temperature range | Almost all colors are warm-muted. There's no cool anchor to create temperature contrast. | Add 1–2 cool-muted anchors (e.g., a slate blue for "background computation" or "inactive" states) to make the warm tones feel deliberate rather than monochrome. |
| Focus color saturation | `state.focus` (#C8643F) is the only relatively saturated color. It works but could be more decisive. | Slightly deepen the focus rust to increase the contrast between active and inactive states. The current focus-to-paper contrast ratio should be verified. |
| Evidence fill/stroke pairs | Six pairs follow the same pattern (fill: light tint, stroke: darker). This is systematic but can feel formulaic. | Vary one pair (e.g., failure) to break the pattern — darker fill, lighter stroke — to signal category difference. |
| Rigid-set palette beyond 15 | 15 colors defined. What happens with 16+ rigid sets? | Define a wrapping or variation strategy: desaturate further, add pattern, or use a second hue rotation. |
| Dark mode | No dark mode tokens. | Not urgent — the atelier thesis is inherently light-background. A dark variant would need its own thesis. |

**Verdict:** The palette is the most mature part of the aesthetic system. The
gaps are refinement, not redesign.

---

## 3. Visual Artifact Quality — Developing, Uneven

### VE-001: Figure 72 (Integrated Showcase)

A multi-panel scientific figure. Browser-composed, tokenized, screenshot-
baselined.

**Strengths:**
- Evidence domains are visually distinct
- The figure pipeline (YAML spec → HTML → PNG/PDF → QA) is repeatable
- Art Director review artifact exists

**Weaknesses:**
- The figure is dense — 7+ panels. A reader may not know where to look first.
- Browser-composed figures can render differently across browsers and font
  availability. The "Anthropic Sans, Inter, Segoe UI" font stack is a
  workaround, not a solution.
- No evidence of the figure being tested at A4 print size.

**Improvement:** Add a "reading order" annotation (numbered panels or a visual
flow line). Test the figure at 300 DPI A4 print and fix any legibility issues.

### VE-002: Viewer Canvas Evidence

A TkAgg canvas contact sheet showing four viewer states.

**Strengths:**
- Proves the viewer projection path works end-to-end
- Screenshot-baselined (pixel-hash verified)

**Weaknesses:**
- TkAgg canvas rendering quality is limited by Tkinter — anti-aliasing,
  subpixel rendering, and font hinting are OS-dependent and not controllable
- The contact sheet format is useful for QA but doesn't showcase the viewer's
  interactive experience
- No full-window screenshot with panels and inspector visible — the canvas is
  seen in isolation

**Improvement:** Capture a full-window screenshot (canvas + inspector + status
bar) at a standard resolution. This is the "what the user actually sees" view
and is more valuable for aesthetic judgment than a canvas-only contact sheet.

### Taste Seed Image

The single curve on A4 paper.

**Strengths:**
- Pure expression of the thesis — nothing to remove
- A4 proportion, warm paper, tapered stroke, asymmetric composition
- Serves as calibration target: "are we closer to this or farther?"

**Weaknesses:**
- Not connected to any pipeline — it's a static image, not a generated figure
- The curve has no semantic meaning (intentional, but limits its use as a
  reference beyond "this is our taste")

**Improvement:** Create one more taste seed that bridges the gap between "pure
taste" and "solver evidence" — e.g., the same A4 paper with a simple
geometric constraint graph rendered in the GCS palette, still minimal, still
quiet, but now carrying solver meaning.

---

## 4. Implementation vs. Thesis Gap Analysis

| Thesis claim | Implementation status | Gap |
| --- | --- | --- |
| "Warm technical neutrals" | Palette defined. Applied to Tkinter and Matplotlib. | Full — no gap. |
| "Color carries semantic weight" | Evidence domain colors, state colors, rigid-set palette all semantic. | Minor — some semantic colors (e.g., evidence.graph.fill vs evidence.planner.fill) are hard to distinguish at small size. |
| "Geometry and constraints remain inspectable" | Geometry markers and constraint line styles are distinct. | Moderate — the current viewer renders constraints as lines; it's not always obvious which constraint connects which entities. |
| "Dense model data stays scannable" | Inspector layout is defined (Phase 3) but not yet implemented. | Significant — the current viewer uses stacked debug panels, not the tabbed inspector design. |
| "Replay and solve feedback feel deliberate" | Replay rail defined (Phase 4) but not yet implemented. | Significant — replay currently works through the CLI and JSON, not through the viewer's visual feedback. |
| "Tkinter and Matplotlib share one visual language" | Shared `color_scheme.py` tokens. | Full — no gap. |
| "Surfaces flat with thin borders" | `rule.default` (#D8D1C4), `rule.soft` (#ECE7DD) defined. | Full — no gap in tokens. Application coverage unknown. |
| "UI controls dense but quiet" | Defined in principle but not audited. | Unknown — no UI density audit has been performed. |

**Biggest gap:** Phases 3–5 of the aesthetic roadmap (Inspector Layout, Replay
Polish, Design QA) are designed but not implemented. The current viewer uses
the Phase 1 theme foundation on the pre-existing layout. The aesthetic thesis
is visible in the colors but not yet in the spatial organization.

---

## 5. Concrete Improvement Opportunities

Ordered by impact-to-effort ratio (highest first).

### Immediate (do in any session, no code change)

**A1. Create a "bridge" taste seed.**

Generate a second image: same A4 paper, same warm white, but this time render
a simple 3-point, 2-constraint geometric scene in the GCS palette. The curve
becomes a constraint graph. The taste seed gains semantic content without
losing restraint.

This closes the gap between "our taste on a blank page" and "our taste with
solver evidence on the page."

**A2. Full-window viewer screenshot.**

Capture the current viewer at a standard resolution (1920×1080 or 1600×900)
with a scene loaded, inspector visible, canvas visible, status bar visible.
Add to VE-002 as a companion artifact. This is the "what does it actually look
like" reference that the canvas-only contact sheet doesn't provide.

### Short-term (1–2 sessions, code change)

**A3. Audit and tighten the color palette temperature range.**

Add 1–2 cool-muted tokens:
- `surface.cool.muted` — a desaturated slate blue-gray for computational
  background states
- `state.inactive` — a cool gray for non-interactive elements

This makes the warm tones feel intentional (contrast) rather than monochrome
(absence of cool tones).

**A4. Verify contrast ratios for accessibility.**

Run the color tokens through a contrast checker:
- Text on surface: `text.primary` (#181715) on `surface.paper` (#F7F4EC) →
  contrast ratio
- Focus text: `state.text.focus` (#87412F) on `surface.panel` (#FFFEFA) →
  contrast ratio
- Error text: `state.text.error` (#8F352F) on `surface.panel` → contrast ratio

Document any tokens that fall below WCAG AA (4.5:1 for normal text, 3:1 for
large text).

### Medium-term (3–8 weeks, aligned with aesthetic roadmap phases)

**A5. Implement Phase 3 (Inspector Layout).**

This is the highest-impact single change for closing the thesis-implementation
gap. The tabbed inspector replaces stacked debug panels and directly addresses
the "dense model data stays scannable" claim.

**A6. Implement Phase 4 (Replay Polish).**

Replay rail near the viewport. Current replay action highlight. This addresses
the "replay and solve feedback feel deliberate" claim.

### Long-term (2–6 months)

**A7. Publish a visual identity brief.**

Extract the key visual decisions (palette, typography, spacing, do/don't) into
a single document that an external contributor can read in 5 minutes. This is
the aesthetic equivalent of the 20-minute contributor path.

**A8. Build a figure gallery.**

Collect the strongest figures (Figure 72, Figure 95, taste seeds, viewer
screenshots) into a single browser-navigable page. This is the aesthetic
portfolio — a reviewer can see the visual range of the project in one scroll.

---

## 6. Aesthetic Maturity Self-Assessment

| Dimension | Level | Evidence |
| --- | --- | --- |
| Visual thesis clarity | Strong | "Quiet Technical Atelier" is stated, principles are enumerated, taste seed exists |
| Color system maturity | Strong | 100 named tokens, semantic mapping, shared across Tkinter and Matplotlib |
| Typography | Adequate | Sans/serif split defined; font stack depends on system availability |
| Spatial design (layout) | Early | Phases 3–4 designed but not implemented; current layout is functional but not designed |
| Motion/interaction design | Not started | No animation, transition, or interaction-state design exists |
| Visual QA automation | Strong | Screenshot baselines, text overflow, overlap/contrast, token lint — all automated |
| External aesthetic legibility | Early | Taste seed exists; no external reviewer has seen it; no visual identity brief exists |
| Figure pipeline maturity | Strong | YAML spec → HTML → PNG/PDF → QA → review → publication — repeatable and spec-driven |

**Overall:** The color system and thesis are strong. The figure pipeline is
strong. The spatial and interaction design are early. The biggest aesthetic
risk is not ugliness — it's that the colors are more refined than the layout
they're applied to, creating a mismatch between surface quality and structural
quality.

---

## 7. Next Aesthetic Action

The highest-impact aesthetic move available now is **A1 + A2**: create the
bridge taste seed and capture a full-window viewer screenshot. These are
zero-code, high-signal actions that immediately strengthen the aesthetic
evidence portfolio and provide clearer targets for the Phase 3–5
implementation work.
