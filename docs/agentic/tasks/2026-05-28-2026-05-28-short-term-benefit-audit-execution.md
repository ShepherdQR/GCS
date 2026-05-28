---
task_id: 2026-05-28-short-term-benefit-audit-execution
status: complete
request: "Execute all 4 short-term benefit audit roadmap items: S1 activate cost_per_commit baseline (relax n≥5→n≥3), S2 multi-project data import, S3 BEI knowledge_score threshold calibration, S4 snap --trend enhancement"
scope: tool
risk: low
owning_agent: gcs-token-audit-steward
specialist_agents:
  - none
affected_contracts:
  - none
affected_paths:
  - tools/token_audit/db.py
  - tools/token_audit/cli.py
  - tools/token_audit/bei_engine.py
required_evidence:
  - validate-docs
  - compile check
  - baseline calibrate output
  - snap --trend output
human_gate_required: false
human_gate_reason: ""
---

# 2026-05-28-short-term-benefit-audit-execution

## Scope

Execute all 4 short-term items from the session benefit audit roadmap
(`docs/reports/session-benefit-audit-roadmap-2026-05-28.md`):

1. **S1** — Relax cost_per_commit baseline n≥5→n≥3 with "low confidence" marker
2. **S2** — Multi-project data import (`db import --all-projects`)
3. **S3** — BEI knowledge_score threshold calibration (memory_entries_p90 + skill_invocations_p90)
4. **S4** — snap --trend enhancement (this session vs 7-day average)

## Evidence Bundle

- **S1**: `calibrate_baselines()` cost_per_commit threshold changed 5→3, confidence field added;
  CLI shows `[LOW CONFIDENCE]` tag; message updated to "need >=3 sessions".
  Currently no sessions have commits_count>0, baseline will activate as data accumulates.
- **S2**: `db import --all-projects` — 16 sessions already in DB (stop hook auto-import),
  0 new imports needed. Idempotent.
- **S3**: `memory_entries_p90` and `skill_invocations_p90` added to `calibrate_baselines()`;
  `bei_engine._knowledge_score()` now prefers DB-calibrated P90 over config hardcoded values.
  Verified: `skill_invocations_p90` active (n=5).
- **S4**: `snap --trend` shows BEI/Cost/Tokens/Cache vs 7-day average with ↑↓→ arrows.
  JSON output includes `trend` block. Verified output correct.
- validate-docs: passed
- compile check: passed (all 3 files)

## Changed Files

| File | Change |
|------|--------|
| `tools/token_audit/db.py` | S1: cost_per_commit n≥5→≥3 + confidence; S3: +memory_entries_p90 +skill_invocations_p90 |
| `tools/token_audit/cli.py` | S1: baseline calibrate shows confidence; S4: snap --trend flag + _compute_7day_averages + _trend_arrow |
| `tools/token_audit/bei_engine.py` | S3: _knowledge_score prefers DB-calibrated P90 over config |

## Residual Risks

- cost_per_commit baseline still inactive: 0 sessions with commits_count>0 in DB.
  Will auto-activate when 3+ sessions accumulate commit data.
- memory_entries_p90 not yet active (need 5+ sessions with non-empty memory_entries).
  Currently GCS-A sessions have empty memory_entries JSON arrays.
- snap --trend arrow characters render correctly in modern terminals but may
  display as boxes in legacy Windows consoles.

## Non-Goals

- Do not change solver runtime semantics.
- Do not modify the BEI scoring formula or weights.
- Do not add new CLI commands beyond the planned --trend flag.

## Acceptance Gates

- [x] S1: cost_per_commit threshold relaxed to 3 with confidence marker
- [x] S2: db import --all-projects runs idempotently
- [x] S3: knowledge_score consumes DB-calibrated P90 when available
- [x] S4: snap --trend displays 4-metric comparison vs 7-day average
- [x] Python compile check passes
- [x] validate-docs passes

## Verification Plan

```bat
python -m compileall -q tools/token_audit/
python -m tools.token_audit baseline calibrate
python -m tools.token_audit snap --trend
python -m tools.token_audit snap --trend --format json
python tools/agentic_design/agentic_toolkit.py validate-docs
```
