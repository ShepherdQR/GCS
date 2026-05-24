# Experience Forging Note: P5.4 Screenshot Baselines

Date: 2026-05-24

Role: `Bladesmith Quench-Forge`

Status: reusable

## Source Scope

- Session/task: `2026-05-24-p5-4-screenshot-baselines`
- Time range: P5.4 screenshot baseline implementation
- Source artifacts:
  - `docs/architecture/70-visualization/assets/screenshot-baselines.json`
  - `tools/ui_qa/gcs_screenshot_baseline.py`
  - `tests/tools/test_gcs_screenshot_baseline.py`
  - `docs/architecture/70-visualization/screenshot-baseline-gate.md`
  - `docs/completed-tasks/2026-05-24-p5-4-screenshot-baselines/README.md`

## Raw Material Classification

| Type | Notes |
| --- | --- |
| Facts | Figure 71 review PNG is 1600x2200, 281703 bytes, and has a pinned SHA256 digest. |
| Decisions | Use exact PNG digest baselines before adopting pixel-diff tooling. |
| Preferences | Baseline updates must carry task, archive, validation, and roadmap evidence. |
| Hypotheses | A manifest-first policy will make future perceptual diff tooling easier to govern. |
| Open questions | Which viewer GUI states should become the next screenshot baselines. |

## Forged Lessons

| Lesson | Trigger | Action | Guardrail | Evidence | Boundary |
| --- | --- | --- | --- | --- | --- |
| Start screenshot QA with a manifest, not a service. | The repo has a stable PNG artifact but no visual-regression backend. | Pin dimensions, bytes, and SHA256 in a committed manifest. | Do not claim perceptual equivalence from exact hash checks. | `gcs_screenshot_baseline.py` validates the Figure 71 baseline. | Ends when acceptable small pixel drift is needed. |
| Make baseline changes explain themselves. | A screenshot digest will change whenever rendering changes. | Require task archive, validation evidence, and roadmap notes with baseline updates. | Do not update hashes as a mechanical fix. | The P5.4 gate doc records the change rule. | Applies to stable review artifacts. |

## Rejected Generalizations

| Claim | Why rejected or provisional | Evidence needed |
| --- | --- | --- |
| "Screenshot QA requires a new hosted visual regression tool." | P5.4 can establish the contract with repo-native metadata first. | Need multiple baselines and tolerance needs before adding a service. |
| "Exact hashes are enough forever." | They are intentionally strict and brittle under valid renderer changes. | Future perceptual diff or pixel comparison policy. |

## Recommended Promotion

Choose one:

- update a checklist.

Rationale:

Every stable visual artifact should have a manifest entry before a heavier
visual-regression backend is considered.

## Follow-Up

- Add viewer-state baselines only after the first figure baseline process is
  stable.
- Reuse the manifest if a future browser or Figma export backend is adopted.
