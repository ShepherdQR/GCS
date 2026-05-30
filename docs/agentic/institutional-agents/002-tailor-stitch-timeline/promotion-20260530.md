# I002 Tailor: Promotion Review — 2026-05-30

## Summary

Formal promotion review for I002 Tailor (裁缝: 裁剪-缝合 / Stitch-Timeline).
The agent was at Practiced, promoted seed (8/10). This review evaluates it
against the Promoted criteria.

## Promotion Criteria (from scorecard)

A role is ready for Promoted when it has:
1. A recurring trigger — YES. Tailor is invoked every 3-5 related sessions.
2. A bounded decision surface — YES. Guardrails and handoff rules are explicit.
3. A prompt and output template — YES. `prompts/invoke.md` and `templates/timeline-entry.md`.
4. At least one negative or refusal eval — YES. `evals/refuse-invented-causality.md`.
5. Enough real examples — YES. 6 timeline examples across multiple threads.

## Evidence Table

| Example | Date | Thread |
|---------|------|--------|
| 本地仓库缝合时间线 | 2026-05-24 | Repository state |
| 仓库清理时间线 | 2026-05-25 | Repository hygiene |
| Git session branch 清理时间线 | 2026-05-26 | Git governance |
| Git stitch 与 AI governance 时间线 | 2026-05-26 | AI governance |
| Solver Steps 52-55 时间线 | 2026-05-30 | Solver/architecture |
| Scene generation testing pipeline 时间线 | 2026-05-30 | Testing/fixture pipeline |

Threads covered: repository state, git governance, AI governance, solver
architecture, testing pipeline. Meets the scorecard's recommendation to
"add separate architecture, agentic-SE, and fixture timeline examples."

## Score Dimension Review

| Dimension | Score | Rationale |
|-----------|------:|-----------|
| Contract clarity | 2/2 | Mission, trigger, inputs, outputs, and guardrails explicit in README. |
| Prompt usability | 1/1 | `prompts/invoke.md` is copyable and scoped. |
| Template usability | 1/1 | `templates/timeline-entry.md` is durable for later sessions. |
| Eval or refusal coverage | 2/2 | Refusal eval prevents invented causality. |
| Example evidence | 2/2 | 6 real examples across 4+ threads. Evidence is distributed. |
| Boundary discipline | 1/1 | README handoff table defines 7 escalation paths. |
| Index discoverability | 1/1 | Listed in registry, scorecard, agent inventory, and `.claude/agents/`. |
| **Total** | **10/10** | Was 8/10 before example diversity was demonstrated. |

## Decision

**Promote to Promoted (score 10/10).**

I002 Tailor is the second Promoted institutional agent after I001 Bladesmith.
It has demonstrated the ability to stitch timelines across repository state,
git governance, AI governance, solver architecture, and testing pipeline
threads. The 6 real examples show sustained value, not a one-off pattern.

## Post-Promotion Notes

- Tailor's main risk remains invented causality. The refusal eval
  (`refuse-invented-causality.md`) should be exercised on a real ambiguous
  timeline situation to harden this boundary.
- Tailor should now be referenced from the lifecycle runbook as a recommended
  post-arc action (every 3-5 related sessions, per OPERATING-STANDARD.md).
- Next maturity gate: Institutional — requires ownership, operating standard
  reference, and automated or scheduled invocation.

## Registry Update Required

- `docs/agentic/institutional-agent-registry-and-scorecard.md`: I002 maturity → Promoted, score → 10/10.
- `docs/agentic/institutional-agents/README.md`: I002 status → Promoted.
- `docs/agentic/agent-skill-asset-inventory.md`: I002 maturity → Promoted.
