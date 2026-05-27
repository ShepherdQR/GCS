# Long-Term Weak Line Development — Detailed Design

Date: 2026-05-27
Status: active
Depends on: `docs/architecture/100-medium-term-design.md` (medium-term items complete or in progress)

## Purpose

This document provides detailed design for the 5 long-term items. Each depends
on medium-term completions and/or external human responses. The designs are
intentionally parametric — they describe what success looks like and what to do
when the dependency resolves, rather than prescribing dates.

---

## L1. Archive a Real External Review or Contribution

**Narrative lines:** 11. Product/user/market story; 14. Business/open-source strategy
**Depends on:** M2 (first review packet sent and responded to)
**Time horizon:** 1–3 months after M2

### Design

**Archive structure:**

```
docs/product/reviews/
├── packets/
│   └── 001-researcher-review/    # M2 output
├── 001-<researcher>-<date>.md    # L1 output
└── REVIEW_INDEX.md               # Index of all reviews
```

**Review archive template:**

```markdown
# Review 001: <Researcher Name or Anonymized Label> — <Date>

## Reviewer Context
- Field: <computational geometry / CAD / scientific computing / other>
- Affiliation: <university / company / independent>
- How they found GCS: <sent packet / found on GitHub / conference / other>

## What They Did
- [ ] Ran D1 CLI smoke
- [ ] Read D6 evidence walkthrough
- [ ] Ran the solver on their own scene
- [ ] Provided written feedback
- [ ] Opened an issue
- [ ] Submitted a PR

## Response Summary
<Direct quotes (anonymized if needed) or paraphrased key points>

## What We Learned
<3–5 actionable insights>

## What Changed
<Specific commits, doc updates, or design decisions triggered by this review>

## Follow-up
<What we owe the reviewer, if anything>
```

**Success criteria (in order of increasing value):**

1. **Minimal:** Review packet sent, response received, archive created
2. **Good:** Response contains at least one criticism or confusion that leads
   to a doc fix or UX improvement
3. **Strong:** Reviewer runs GCS on their own scene and reports results
4. **Ideal:** Reviewer contributes a fix, a scene, or a suggestion that becomes
   a committed change

**Risk:** M2 may get no response. Mitigation: send to 3 researchers (not 1).
If all 3 don't respond in 4 weeks, the review packet itself becomes the
artifact and the narrative lines remain at "Strong but split" until external
contact happens through other channels (conference, publication, social).

**Verification:**
```bat
type docs\product\reviews\REVIEW_INDEX.md
# At least one entry with all sections filled
```

---

## L2. Promote a Second Institutional Agent; Establish Promotion Rhythm

**Narrative lines:** 9. Institutional agents and learning
**Depends on:** S5 (I001 Bladesmith promoted); accumulated agent usage across
multiple sessions
**Time horizon:** 1–3 months after S5

### Design

**Candidate ranking (most likely to promote next):**

| Rank | Agent | Current maturity | Score | Gap to Promoted |
| --- | --- | --- | ---: | --- |
| 1 | I002 Tailor: Stitch-Timeline | Practiced, promoted seed | 8/10 | Needs more timeline examples across divergent threads (architecture, agentic-SE, fixture) |
| 2 | I003 Atelier Steward: Calibrate-Review | Seed | 6/10 | Needs 2 more UI/figure reviews; then Practiced; then Promoted (longer path) |
| 3 | I004 Art Director: Frame-Judge | Seed | 6/10 | Needs more rendered-artifact evidence; parallel path to I003 |

**Recommended target:** I002 Tailor.

Rationale:
- Already at "Practiced, promoted seed" with 4 timeline examples
- Promotion gap is specific and achievable: add architecture, agentic-SE, and
  fixture timeline examples (3 more sessions with distinct thread focus)
- Scorecard is strong (8/10 vs. I001's pre-promotion 9/10)
- Refusal eval exists: "refuse to merge two adjacent events into one causal
  story when the archives do not support that connection"

**Promotion rhythm definition:**

After two promotions, analyze:
- Time between S5 (I001) and L2 (I002) promotions
- Number of sessions between promotions
- Whether the second promotion was easier (scorecard refinement) or harder
  (higher bar)

Document the rhythm in a new section of the agent registry:
`## Promotion Rhythm`.

**Acceptance criteria:**
- I002 Tailor status is "Promoted"
- `docs/agentic/institutional-agent-registry-and-scorecard.md` has a
  "Promotion Rhythm" section with: dates of first two promotions, sessions
  between them, refined criteria (if any), and projected next promotion
  candidate
- Promotion criteria are stable enough that a new reviewer can apply them

**Verification:**
```bat
type docs\agentic\institutional-agent-registry-and-scorecard.md
# Registry shows I002 at Promoted; Promotion Rhythm section exists
```

---

## L3. Publish the First Public Release Snapshot

**Narrative lines:** 12. Release/packaging/onboarding; 14. Business/open-source
**Depends on:** S3 (R2 build transcript), M4 (replay checker in release gate),
M1 (external baseline comparison note)
**Time horizon:** 1–2 months after M4 and M1 complete

### Design

**Release artifact checklist:**

| # | Artifact | Status (2026-05-27) | Owner |
| --- | --- | --- | --- |
| 1 | Tagged version (v0.1.0) | Not created | Release owner |
| 2 | Build transcript | S3 complete | Release owner |
| 3 | Contract test pass (115/115) | S3 verified | Solver |
| 4 | Replay checker pass in smoke gate | M4 pending | Release owner |
| 5 | External baseline comparison note | M1 pending | Benchmark |
| 6 | README with 5-minute quickstart | Partial | Product |
| 7 | D1–D6 demo packages current | S2 complete (D6) | Product |
| 8 | Release notes (`CHANGELOG.md` or `RELEASE.md`) | Not created | Release owner |
| 9 | Known limitations documented | Partial | Architecture |

**Release tag format:** `v0.1.0` (semantic versioning, 0.x.y = pre-stable)

**Release notes structure:**
```markdown
# GCS v0.1.0 — Researcher Preview

## What GCS Is
<One paragraph>

## What's In This Release
- CLI solver with diagnostic reports
- 5 built-in constraint types
- 115 contract tests (100% pass)
- Replay evidence with schema-aware checker
- Python viewer with diagnostic overlays
- 6 demo packages (D1–D6)

## Quickstart
```bat
scripts\build_clang_ninja.cmd
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt
```

## Known Limitations
- 5 constraint types (FreeCAD Sketcher has 10+)
- Windows-only build (Clang 20, CMake 4.3)
- No GUI scene editor (viewer is read-only projection)
- Replay schema not yet stabilized across releases

## What's Next
- R3: additional constraint types, cross-platform build
- B2: external baseline comparison suite
- D7: live workbench walkthrough
```

**Verification:**
```bat
git tag -l "v0.1.0"
# Tag exists
gh release view v0.1.0
# Release page has all checklist items
```

---

## L4. Build a Contribution Workflow Example

**Narrative lines:** 14. Business/open-source; 6. Agentic-SE operating layer
**Depends on:** L1 (real external review or contribution) or a simulated
walkthrough if L1 hasn't produced a contribution
**Time horizon:** 2–4 months after L1

### Design

**Document:** `docs/product/contribution-workflow.md`

**Structure:**

```markdown
# Contribution Workflow

## Before You Start
- Read the contribution boundary: docs/product/researcher-contribution-boundary.md
- Understand what GCS is and is not

## Ways to Contribute

### Level 1: Report a Finding
- Open an issue
- Include: GCS version, scene file, expected vs actual output
- Template: .github/ISSUE_TEMPLATE/solver-finding.md

### Level 2: Submit a Scene
- Add a fixture to fixtures/scene/community/
- Include: scene file, expected behavior, why it's interesting
- PR template: .github/PULL_REQUEST_TEMPLATE/community-scene.md

### Level 3: Submit a Code Change
- Scope: one module, one concern
- Pass: contract tests, module dependency check, quality gate
- PR description: what, why, evidence (screenshot or command output)
- Review: a maintainer will review within <timeframe>

## Gates Your Change Must Pass
1. build_clang_ninja.cmd (no new warnings)
2. ctest --test-dir out/build/clang-ninja (all contract tests)
3. python tools/agentic_design/agentic_toolkit.py validate-docs
4. E-GOV-001 staging validator (scoped files only)

## What Happens After You Submit
1. Automated gates run (if CI is configured)
2. A maintainer reviews within <timeframe>
3. Feedback is given via PR comments
4. Once approved, your change is merged

## Community Scenes
<Link to fixtures/scene/community/ and how to submit>
```

**Key design decisions:**
- The external workflow is a simplified subset of the internal task lifecycle
- No task card required for external contributors (too heavy)
- Same quality gates as internal work (build, tests, validate-docs)
- PR template guides the contributor to provide evidence (screenshot, output)
- Explicit about response timeframes ("within 2 weeks")

**Verification:**
```bat
type docs\product\contribution-workflow.md
# All sections present; a new reader can understand how to contribute
```

---

## L5. Establish Trend Lines Across Multiple Narrative Dimensions

**Narrative lines:** 7. Quality gates (primary); All (secondary)
**Depends on:** S4 (first 3 trend entries); 10+ task closures across multiple
narrative lines
**Time horizon:** 3–6 months of sustained work

### Design

**Trend data model:**

The metrics dashboard trend table grows from 3 rows (S4) to 15+ rows. Each row
captures:

| Field | Type | Example |
| --- | --- | --- |
| Date | ISO 8601 | 2026-06-15 |
| Task | Slug | m1-external-baseline |
| Narrative line(s) affected | List | 13, 14 |
| Validate-docs | PASS/FAIL/SKIP | PASS |
| Contract tests | N/N passed | 115/115 |
| New capability demonstrated | Free text | First external baseline comparison |
| Weak line movement | None/Slight/Moderate/Significant | Moderate (line 13) |

**Figure 95 trend update:**

When L5 triggers (10+ entries), regenerate Figure 95 to show the movement of
weak lines. The updated SVG should show:

- At least 2 lines moved from "Developing" or "Strong but split" to "Strong"
- New data points for the lines that haven't moved (with explanation)
- Updated trend brief at `docs/architecture/70-visualization/narrative-line-level-trend-<date>.md`

**Acceptance:** A viewer of the Figure 95 trend SVG can see:
- Which lines moved (visual: arrow or color change)
- When they moved (visual: date label)
- What evidence caused the movement (link to capability demonstration)

**Verification:**
```bat
type docs\agentic\metrics-dashboard.md
# Trend table has 10+ rows
# At least 2 entries show "Significant" weak line movement
type docs\architecture\70-visualization\narrative-line-level-trend-<date>.md
# Updated trend brief with movement evidence
```

---

## Long-Term Dependency Graph

```
M2 ──► L1 (external review)
M1 ──► L3 (public release)
M4 ──► L3
S5 ──► L2 (second agent promotion)
L1 ──► L4 (contribution workflow)
S4 ──► L5 (multi-dimension trends)

L3 + L4 + L5 ──► "Very Strong" status for 3+ weak lines
```

## Rhythm

| Review point | What to check |
| --- | --- |
| Monthly | Are medium-term items completing? Are any long-term dependencies resolving? |
| After each medium-term completion | Is the corresponding long-term item now unblocked? |
| After each external contact | Does L1 have enough material for an archive? |
| After 10 task closures | Does L5 have enough data for a trend update? |
