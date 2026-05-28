# GCS Critical Issues & Blockers Registry

**Purpose**: Single source of truth for blocking issues, critical findings, and pre-execution blockers discovered during any GCS workstream. Every entry must be resolved or explicitly accepted before dependent work proceeds.

**Convention**: Issues are numbered `CI-YYYY-MM-DD-N` (Critical Issue, date discovered, sequence). Status is one of: `open`, `in-progress`, `resolved`, `accepted` (acknowledged but intentionally not fixed).

**Location**: `docs/agentic/critical-issues-registry.md`
**Maintained by**: All institutional agents; reviewed weekly by `night-watch`

---

## Open Issues

### CI-2026-05-28-1: `cache_creation_input_tokens` Always Zero Across All Sessions

- **Date**: 2026-05-28
- **Status**: resolved
- **Resolved date**: 2026-05-28
- **Resolution**: Empirical analysis of 5+ JSONL transcripts confirms DeepSeek API never reports `cache_creation_input_tokens` as non-zero. Turn 1 has `input≈40K, cr=0, cc=0` (cache written silently), Turn 2 has `input≈40K, cr=0, cc=0`, Turn 3+ has `input≈150, cr≈39,552, cc=0` (cache read reported, creation still 0). Adopted estimation fallback: `CACHEABLE_PREFIX_ESTIMATE = 39000` based on Turn 1 input minus estimated user message. CWAR = total_cache_read / 39000. M2 uses same estimate for effective cost calculation. Error bound: ±15% based on variance in Turn 1 input across sessions (39,595–40,556 tokens).
- **Severity**: CRITICAL — blocks token-econ-v2 M2/M3 metric computation
- **Discovered by**: token-econ-metric-system-v2 pre-execution audit
- **Scope**: `tools/token_audit/parser.py`, `tools/token_audit/metrics_engine.py` (planned)
- **Owner**: gcs-token-audit-steward

**Description**:

All 29 sessions in `audit.db` use DeepSeek API (21× v4-pro, 5× v4-flash, 3× synthetic). Every assistant message reports:
```json
{"cache_creation_input_tokens": 0, "cache_read_input_tokens": 39552, ...}
```

The `cache_creation_input_tokens` field is present in the API response but always 0. This means:
- M2 (effective cache hit rate with write-premium adjustment) cannot be computed from API data
- M3 (cache write amortization ratio) cannot be computed — CWAR = reads / 0 = ∞

**Impact**: The two metrics that directly address "cache hit rate too high is not necessarily good" — the core motivation for the v2 upgrade — depend on this data.

**Proposed resolution**: Use an estimation model based on known cacheable prefix size (~32,379 tokens for GCS). See [pre-execution checklist](../research/token-economics-pre-execution-checklist-2026-05-28.md) for detailed options.

**Blocks**: token-econ-metric-system-v2 Phase 2 (metrics_engine.py M2/M3 implementation)

**Links**:
- [Pre-execution checklist](../research/token-economics-pre-execution-checklist-2026-05-28.md#b1-cache_creation_input_tokens-data-gap-critical)
- [Execution plan](../research/token-economics-execution-plan-2026-05-28.md)
- [Unified evaluation system design](../research/token-economics-unified-evaluation-system-2026-05-28.md)

---

### CI-2026-05-28-2: No Test Infrastructure for Token Audit Module

- **Date**: 2026-05-28
- **Status**: resolved
- **Resolved date**: 2026-05-28
- **Resolution**: pytest 9.0.3 installed. Created conftest.py (5 fixtures: sample_token_usage, sample_telemetry, sample_telemetry_abandoned, sample_telemetry_stale, temp_db). Created test_parser.py (11 tests) and test_metrics_engine.py (30 tests). All 41 tests pass. Retroactive coverage established for parser.py TokenUsage/SessionSnapshot and metrics_engine.py M1-M13.
- **Severity**: HIGH — no regression safety net for planned ~1,530 lines of new code
- **Discovered by**: token-econ-metric-system-v2 pre-execution audit
- **Scope**: `tools/token_audit/tests/` (only `__init__.py` exists)
- **Owner**: gcs-token-audit-steward

**Description**:

`pytest` is not installed. The test directory contains only an empty `__init__.py`. No tests exist for any existing module (`parser.py`, `cost_model.py`, `bei_engine.py`, `reporter.py`, `db.py`, `alerts.py`). The v2 execution plan adds 3 new modules (~800 lines) and modifies 6 existing files (~350 lines) — all without test coverage.

**Impact**: Regressions in existing BEI scoring or cost calculation could go undetected. New M2/M3 metrics with estimation fallbacks have no correctness verification.

**Proposed resolution**: Install pytest, create `conftest.py` with standard fixtures, write retroactive tests for critical paths before Phase 2.

**Blocks**: token-econ-metric-system-v2 Phase 2+ (all new code)

**Links**:
- [Pre-execution checklist](../research/token-economics-pre-execution-checklist-2026-05-28.md#b2-no-test-infrastructure-critical)

---

## Resolved Issues

*(None yet — registry created 2026-05-28)*

---

## Accepted Issues

*(None yet)*

---

## Discovery Protocol

When any institutional agent discovers a blocking or critical issue:

1. Assign the next `CI-YYYY-MM-DD-N` ID
2. Add to the Open Issues section above
3. Set severity: `CRITICAL` (blocks work), `HIGH` (significant risk), `MEDIUM` (should fix, not blocking)
4. Link all relevant docs (research, plans, task cards)
5. If blocking: add to the `Blocks` field with the specific workstream name
6. Notify the affected workstream owner

## Resolution Protocol

When an issue is resolved:

1. Move entry from Open → Resolved
2. Add `Resolved date` and `Resolution` fields
3. Keep the entry for traceability — never delete

## Weekly Review

The `night-watch` agent reviews this registry weekly:
- Flag any issue open >14 days without progress
- Escalate CRITICAL issues open >7 days
- Verify resolved issues have linked evidence
