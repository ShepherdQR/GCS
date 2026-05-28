---
task_id: 2026-05-28-token-econ-metric-system-v2
status: draft
request: "Upgrade token audit system from v1 cost-tracking to v2 multi-dimensional token economic evaluation: 13 derived metrics, 4 composite indices, workload classification, cache health framework, 7 decision rules, enhanced reporter/dashboard. ~1,530 lines across 12 files. Preceded by 3 research reports and a pre-execution checklist."
scope: architecture
risk: medium
owning_agent: gcs-architecture-steward
specialist_agents:
  - none
affected_contracts:
  - none
affected_paths:
  - docs/agentic/
required_evidence:
  - validate-docs
  - validate-inventory
  - check-dependencies
human_gate_required: false
human_gate_reason: ""
---

# 2026-05-28-token-econ-metric-system-v2

## Scope

In scope:
- Phase 1: Schema migration for 10 new columns in `sessions` and `daily_summary` tables
- Phase 2: New `metrics_engine.py` computing M1–M13 derived metrics
- Phase 3: New `composite_indices.py` computing CI-1 through CI-4 with workload classification
- Phase 4: New `decision_engine.py` implementing D1–D7 decision rules
- Phase 5: Enhanced reporter (session diagnostic card, cache health report), CLI updates (`diagnose`, `cache-health` commands), dashboard enhancement
- Backward compatibility: existing BEI scores, reports, and CLI commands continue to work

Intentionally out of scope:
- Real-time streaming metric computation (batch/post-hoc only)
- Cross-project aggregation beyond the existing dashboard
- Integration with external monitoring systems (Grafana, Datadog)
- UI-based dashboard (terminal + Markdown + HTML only)

## Non-Goals

- Do not change solver runtime semantics.
- Do not redefine architecture contracts in `docs/agentic`.

## Context To Read

- `docs/architecture/README.md`
- Owning skill: `gcs-token-audit-steward`

## Acceptance Gates

- The owning boundary is clear.
- Required evidence is produced or a reason is recorded.
- Residual risks are named.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-28-token-econ-metric-system-v2.md
```

## Evidence Bundle

Research reports (completed before task card):
- `docs/research/token-economics-multi-paradigm-analysis-2026-05-28.md` — 7-paradigm industry analysis, 465 lines
- `docs/research/token-economics-unified-evaluation-system-2026-05-28.md` — metric architecture design, 919 lines
- `docs/research/token-economics-execution-plan-2026-05-28.md` — 5-phase execution plan, 1,093 lines
- `docs/research/token-economics-pre-execution-checklist-2026-05-28.md` — 9-item preparation checklist

Pre-execution artifacts:
- `docs/agentic/critical-issues-registry.md` — 2 critical issues registered (CI-2026-05-28-1, CI-2026-05-28-2)
- `tools/token_audit/audit.db.pre-v2-backup` — 110,592 bytes, 29 sessions preserved
- `tools/token_audit/tests/conftest.py` — 5 fixtures (sample_token_usage, sample_telemetry, sample_telemetry_abandoned, sample_telemetry_stale, temp_db)

Verification commands:
```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-28-token-econ-metric-system-v2.md
python -m pytest tools\token_audit\tests\ -v
```

## Residual Risks

1. **CI-2026-05-28-1**: `cache_creation_input_tokens` is always 0 across all DeepSeek sessions. M2/M3 will use estimation fallback (±20% error bound). If Anthropic API is later adopted as primary, the estimation model must be recalibrated.

2. **Workload classification accuracy**: Initial classifier uses heuristics (task card scope + tool call patterns). Edge cases (research-heavy bug fixes, code-heavy architecture sessions) may be misclassified. Mitigation: log classification confidence; allow manual override.

3. **TWR (M7) accuracy**: Token waste ratio estimation uses TLR-based heuristics. Without per-turn semantic analysis, "exploratory" vs "wasted" tokens cannot be distinguished. Acceptable for v2; v3 should add turn-level tracing.

4. **Cold-load overhead estimation**: Fixed at ~32,379 tokens based on char/5 approximation. Real tokenization may vary ±30%. Mitigation: configurable constant; recalibrate after Phase 5.

5. **Baseline calibration period**: After deployment, ATEI and per-workload thresholds will be noisy for ~14 days until sufficient v2 data accumulates. Existing BEI baselines bridge the gap.
