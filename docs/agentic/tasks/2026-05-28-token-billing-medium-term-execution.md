---
task_id: 2026-05-28-token-billing-medium-term-execution
status: complete
request: "Execute 6 medium-term token billing plans: multi-model compare, budget tracking, monthly prediction, batch pricing, cache TTL, routing optimization. Write token billing roadmap S1-L6. Close session."
scope: tool
risk: medium
owning_agent: gcs-token-audit-steward
specialist_agents:
  - none
affected_contracts:
  - none
affected_paths:
  - tools/token_audit/cost_model.py
  - tools/token_audit/reporter.py
  - tools/token_audit/cli.py
  - tools/token_audit/db.py
  - tools/token_audit/config.yaml
  - docs/research/20260528/token-billing-roadmap/README.md
required_evidence:
  - validate-docs
  - compile check passed
  - dashboard tested
  - report --compare tested
  - routing command tested
human_gate_required: false
human_gate_reason: ""
---

# 2026-05-28-token-billing-medium-term-execution

## Scope

Continued from the 2026-05-27 token billing sessions. Executed all 6 medium-term
billing plans designed in the previous chapter: multi-model cost comparison
(--compare), daily/weekly budget tracking in dashboard, monthly cost prediction,
batch API pricing (--batch), cache TTL differentiation (--cache-ttl), and model
routing optimization (routing command). Also wrote a comprehensive S1-L6 roadmap
document covering short/medium/long-term token billing plans.

## Evidence Bundle

- Plan 1: `--compare` flag shows `$0.11 (vs Sonnet $3.32, Opus $5.53)` in reports
- Plan 4/5: Dashboard shows budget + monthly prediction lines
- Plan 2/3: `--batch` and `--cache-ttl` flags threaded through cost calculation
- Plan 6: `routing --days 90` command identifies optimization candidates
- Roadmap: `docs/research/20260528/token-billing-roadmap/README.md` with S1-S5, M1-M5, L1-L6
- All 5 modified files compile clean

## Residual Risks

- Routing classification uses edit_ratio proxy (S4 enhancement pending)
- Comparison models list is hardcoded (S2 config-driven pending)
- Per-chapter cost breakdown schema exists but not yet populated (S1 pending)
