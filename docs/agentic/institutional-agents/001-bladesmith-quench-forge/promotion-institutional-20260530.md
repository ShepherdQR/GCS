# I001 Bladesmith: Quench-Forge — Promotion to Institutional

Date: 2026-05-30
Promotion: Promoted → Institutional

## Evidence Summary

| Requirement | Evidence |
| --- | --- |
| Multiple examples | 20+ forging notes across sessions (2026-05-24 to 2026-05-30), covering visual pipeline, UI QA gates, agentic-SE process, repository hygiene, and replay evidence workflows. |
| Refusal behavior | Two refusal evals: `refuse-unsupported-generalization.md` (prevents one-off observations from becoming project rules) and `refuse-single-session-rule.md` (prevents single-session lessons from becoming permanent rules without a second witness). Both test that the bladesmith separates fact, preference, and hypothesis, and refuses to overclaim authority. |
| Documented ownership | Ownership section in README: the bladesmith self-governs its prompt and template through forging-note patterns; structural role-definition changes require `gcs-architecture-steward` approval. |
| Defined review cadence | Monthly stale-note scan, quarterly prompt/template self-review, on-demand review triggered by any session producing 3+ forging notes. |
| Index discoverability | Listed in institutional-agent registry at Institutional tier; linked from `docs/agentic/institutional-agents/README.md` seed role index; discoverable from experience README and lifecycle runbook. |
| Score | 10/10 (score ceiling reached at Promoted tier; maintained at Institutional) — contract clarity 2/2, prompt usability 1/1, template usability 1/1, eval coverage 2/2, example evidence 2/2, boundary discipline 1/1, index discoverability 1/1. |

## What "Institutional" Means for the Bladesmith

The Bladesmith is no longer a per-session tool or a best-effort practice. It is a
**standing project capability** — a permanent fixture of the GCS agentic
operating layer with ongoing maintenance obligations:

1. **Self-governing, not externally shaped.** The bladesmith modifies its own
   prompt and template when forging-note patterns demand it. No external author
   needs to "fix the bladesmith" — the bladesmith fixes itself through evidence.

2. **Cadenced, not ad-hoc.** The monthly stale-rule scan and quarterly self-review
   mean the bladesmith is not a set-and-forget artifact. It actively maintains the
   quality of its own output over time.

3. **Boundary-enforced, not aspirational.** With two refusal evals and proven
   boundary discipline, the bladesmith reliably declines to create project rules
   without sufficient evidence. This is tested behavior, not a documented intent.

4. **Integrated, not isolated.** The bladesmith's outputs feed into
   `docs/agentic/experience/`, skill candidates, institutional-agent updates,
   checklists, templates, and lifecycle runbook patches. It has material impact
   on how other agents and skills operate.

## Domain Coverage (Maintained from Promoted)

The Bladesmith has forged notes covering:
- Visual pipeline (browser export, figure pipeline, Figma MCP decision)
- UI QA gates (token lint, text overflow, overlap/contrast, screenshot baselines)
- Agentic-SE process (lifecycle, gate policy, eval seeds, skill promotion)
- Repository hygiene (cleanup, fixture hygiene)
- Replay evidence workflow

## Risk Notes

The main governance risk identified at Promoted tier remains valid:
"over-promotion: because it has many examples, it must still separate repeated
pressure from one-off preference." Both refusal evals now directly address this
risk from complementary angles:

- `refuse-unsupported-generalization.md` — blocks one-off observation → project
  rule without evidence breadth.
- `refuse-single-session-rule.md` — blocks single-session success → permanent
  rule without a second confirming witness.

The added review cadence (monthly stale-note scan) provides an additional
safeguard: rules that were well-supported at creation time can be re-examined
when project conditions change.

## Post-Promotion Notes

1. Maintain the monthly review cadence. The first stale-rule scan should happen
   within 30 days (by 2026-06-30).

2. The next useful eval is an **automation hook eval**: test that the bladesmith
   can be triggered automatically by the lifecycle runbook when a session
   produces 3+ forging notes, rather than relying on manual invocation.

3. When a forging note is promoted from "provisional — needs second witness" to
   "durable rule" through a second confirming session, that promotion itself
   should produce a brief note documenting the second witness.

4. Score ceiling reached at 10/10. No further score increase is possible; the
   metric shifts from score growth to cadence maintenance and evidence freshness.
