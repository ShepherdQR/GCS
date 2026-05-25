# S4-05 Institutional-Agent Reassessment

Date: 2026-05-25

## Decision Summary

S4-05 keeps the institutional-agent system small. It upgrades the evidence
status of roles that have real artifacts, keeps visual review roles as seed
packages until they have prompts/templates/evals/examples, and does not create
new standing-agent directories.

| Role | Decision | Evidence | Next Action |
| --- | --- | --- | --- |
| I001 Bladesmith: Quench-Forge | Upgrade to practiced promoted seed. | Prompt, template, refusal eval, and many real forging notes from Step 47 through S3-04. | Keep using for reusable lessons; do not create another lesson-forging role. |
| I002 Tailor: Cut-Stitch Timeline | Upgrade to practiced promoted seed. | Prompt, template, refusal eval, local repo stitch timeline, and repository cleanup timeline. | Use after multi-session or branch-cleanup timelines; add examples only when timeline stitching is actually requested. |
| I003 Atelier Steward: Calibrate-Review | Keep seed. | README exists, but no prompt/template/eval/example package yet. | Add prompt/template/eval only when the next UI or figure governance task needs it. |
| I004 Art Director: Frame-Judge | Keep seed. | README exists, but no prompt/template/eval/example package yet. | Add prompt/template/eval only when a visual artifact needs independent taste review. |
| Candidate roles | Keep candidate. | No repeated real invocation with durable artifacts yet. | Use the role-card generator and fit-check before creating new directories. |

## Rationale

Bladesmith and Tailor now meet the project definition of practiced roles:
each has a role contract, prompt/template/eval material, and more than one real
artifact. They should remain standing agents because they prevent repeated
loss of process knowledge and timeline context.

Atelier Steward and Art Director should not be promoted yet. They are plausible
and useful, but they need concrete visual-governance artifacts before the
project treats them as more than seed roles.

The candidate table should stay a table. E001's active skill covers closure
discipline; it does not justify creating an independent "acceptance officer"
directory without a real independent review artifact.

## Guardrails

- Do not create a new institutional-agent directory without a real use case,
  fit-check, product artifact, and refusal behavior.
- Do not turn Bladesmith into a generic summary role; it must forge reusable
  lessons from evidence.
- Do not turn Tailor into a raw transcript role; it must stitch only durable,
  evidenced timeline events.
- Do not promote visual roles until their first real review artifacts exist.

## Follow-Up

1. Add prompt/template/eval/example packages for I003 or I004 only when a real
   UI or figure task invokes them.
2. Keep candidate roles as candidates until a concrete task proves repeated
   value.
3. Use S2 opt-in gates and the active E001 skill to keep institutional-agent
   artifacts tied to task closure evidence.
