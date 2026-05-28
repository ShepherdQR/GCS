# GCS Token Economic Evaluation System — Pre-Execution Preparation Checklist

**Date**: 2026-05-28
**Scope**: Everything that must be resolved before Phase 1 code changes begin
**Depends on**: [Execution Plan](token-economics-execution-plan-2026-05-28.md)

---

## Preparation Overview

Before writing any code, **9 items** must be resolved. Four are blocking (cannot start without them), five are strongly recommended (will cause rework or bad data if skipped).

---

## BLOCKING — Must Resolve Before Phase 1

### B1: `cache_creation_input_tokens` Data Gap (CRITICAL)

**Problem**: Across all 29 sessions (26 DeepSeek-v4, 3 synthetic/unknown), `cache_creation_input_tokens` is **always 0**. Every single assistant message reports:

```json
{
  "cache_creation_input_tokens": 0,
  "cache_read_input_tokens": 39552,
  "cache_creation": {
    "ephemeral_5m_input_tokens": 0,
    "ephemeral_1h_input_tokens": 0
  }
}
```

This means M2 (effective cache hit rate) and M3 (cache write amortization ratio) — the two metrics that directly address the "cache hit rate too high is not good" problem — **cannot be computed from API data as designed**.

**Root cause analysis** (three hypotheses, need verification):

| Hypothesis | Likelihood | Verification Method |
|-----------|-----------|-------------------|
| DeepSeek API doesn't report `cache_creation_input_tokens` as a separate field | High | Check DeepSeek API docs; test with Anthropic API directly |
| Cache is populated during session init (before JSONL recording starts), so first assistant message already sees it as pre-populated | Medium | Check if ANY message in a fresh session has non-zero cache_creation |
| The field is reported but the JSONL parser doesn't extract it from the right path | Low | Already verified — field is at `message.usage.cache_creation_input_tokens` and is present but 0 |

**Resolution options**:

**Option A (Recommended): Estimate cache_creation from session structure**

Since GCS sessions have a known cacheable prefix structure:
- System tools: ~20,400 tokens (fixed per Claude Code version)
- MCP tools: ~9,100 tokens (fixed per configuration)
- CLAUDE.md: ~784 tokens
- Skill frontmatter: ~1,519 tokens (25 skills × ~60 chars each)
- Agent frontmatter: ~576 tokens (13 agents × ~44 chars each)
- **Total estimated cacheable prefix: ~32,379 tokens**

Each session writes this prefix to cache once (on first turn) and reads it on every subsequent turn. Therefore:

```
estimated_cache_creation_per_session ≈ 32,379  (written once on session init)
actual_cache_read_per_session = Σ cache_read_input_tokens (from all turns)
CWAR = actual_cache_read_per_session / 32,379
```

This gives a conservative (lower-bound) CWAR since it assumes all cacheable tokens are written once per session.

**Option B: Use a calibration factor**

Run a controlled test session against Anthropic API directly (not DeepSeek) to measure the actual ratio of cache_creation to cache_read for a GCS session. Apply that ratio as a calibration factor for DeepSeek sessions.

**Option C: Switch to Anthropic API for one calibration session**

Create a short session using `claude-sonnet-4-6` and capture the real cache_creation values. Use those to validate the estimation model.

**Decision**: Implement Option A as the default, with Option C as a calibration validation step.

**Action items**:
- [ ] Verify with a test Anthropic API call whether `cache_creation_input_tokens` is non-zero
- [ ] If yes: the gap is DeepSeek-specific; document the estimation fallback
- [ ] If no: the gap is in JSONL recording timing; adjust the estimation model
- [ ] Implement `estimate_cache_creation()` function in metrics_engine.py using the ~32,379 token estimate
- [ ] Document the estimation method and its error bounds (±20% estimated)

---

### B2: No Test Infrastructure (CRITICAL)

**Problem**: `pytest` is not installed. The only test file is `tools/token_audit/tests/__init__.py` (empty). No tests exist for any current module.

**Resolution**:

```bash
pip install pytest
```

Then create a minimal test infrastructure before Phase 1:

**File**: `tools/token_audit/tests/conftest.py` (new)
```python
import pytest
import sqlite3
import tempfile
from pathlib import Path

@pytest.fixture
def sample_telemetry():
    """Standard RawTelemetry for testing."""
    from tools.token_audit.metrics_engine import RawTelemetry
    return RawTelemetry(
        input_tokens=50000,
        output_tokens=4000,
        cache_read_tokens=32000,
        cache_creation_tokens=0,  # DeepSeek reality
        estimated_overhead_tokens=32379,
        turn_count=24,
        task_outcome="completed",
        task_type="feature",
        task_risk_level="medium",
        cache_ttl_setting="5min",
    )

@pytest.fixture
def temp_db():
    """In-memory SQLite database with schema."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    schema = Path("tools/token_audit/schema.sql").read_text()
    conn.executescript(schema)
    yield conn
    conn.close()
```

**Action items**:
- [ ] `pip install pytest`
- [ ] Create `conftest.py` with standard fixtures
- [ ] Create `test_parser.py` with basic TokenUsage tests (retroactive)
- [ ] Verify: `python -m pytest tools/token_audit/tests/ -v` runs successfully (even if 0 tests)

---

### B3: Database Backup & Migration Safety (CRITICAL)

**Problem**: The existing `audit.db` contains 29 real sessions with 3.2M tokens of data. Schema migration will add 10 columns. If migration fails, we lose the only historical dataset.

**Resolution**:

```bash
# Backup before any migration
cp tools/token_audit/audit.db tools/token_audit/audit.db.pre-v2-backup

# Test migration on a copy first
cp tools/token_audit/audit.db tools/token_audit/audit.db.test
python -c "
from tools.token_audit.db import init_db
conn = init_db('tools/token_audit/audit.db.test')
# verify new columns exist
cols = [r[1] for r in conn.execute('PRAGMA table_info(sessions)').fetchall()]
print('Columns after migration:', len(cols))
# verify old data intact
count = conn.execute('SELECT COUNT(*) FROM sessions').fetchone()[0]
print(f'Sessions: {count}')
conn.close()
"
```

**Action items**:
- [ ] Create backup: `audit.db.pre-v2-backup`
- [ ] Test migration on copy, verify no data loss
- [ ] Add migration rollback instructions to the execution plan

---

### B4: Task Card Creation (Process Requirement)

**Problem**: CLAUDE.md line 34: "Before mutating files for non-trivial work, create a task card." This is a multi-phase, multi-file implementation — it definitely requires a task card.

**Resolution**:

```bash
python tools/agentic_design/agentic_toolkit.py new-task-card \
  --slug token-econ-metric-system-v2 \
  --scope architecture \
  --risk medium \
  --owner gcs-token-audit-steward \
  --request "Upgrade token audit system from v1 cost-tracking to v2 multi-dimensional token economic evaluation: 13 derived metrics (M1-M13), 4 composite indices (CI-1 to CI-4), workload classification (8 categories), cache health framework (3D: Efficiency × Freshness × Economics), 7 decision rules (D1-D7), enhanced reporter/dashboard. ~1,530 lines across 12 files." \
  --write

python tools/agentic_design/agentic_toolkit.py validate-task-card docs/agentic/tasks/token-econ-metric-system-v2.md
```

**Action items**:
- [ ] Create and validate the task card
- [ ] Link the three research docs from the task card

---

## STRONGLY RECOMMENDED — Resolve Before Phase 2+

### R1: Dirty Working Tree Cleanup

**Problem**: 8 uncommitted changes in the working tree, including 4 modified files unrelated to token economics.

```
M .claude/agents/README.md
M .claude/agents/bladesmith-quench-forge.md
M .claude/skills/README.md
M docs/agentic/institutional-agent-registry-and-scorecard.md
M docs/agentic/institutional-agents/README.md
?? docs/agentic/agent-skill-asset-inventory.md
?? docs/research/token-economics-*.md (3 files)
```

**Resolution**:
- Option A: Commit unrelated changes first, then start token work on clean tree
- Option B: Stash unrelated changes, work on token changes, unstash after

**Recommendation**: Option A. Commit the agent/skill README changes and the research docs separately, then start Phase 1 on a clean tree.

**Action items**:
- [ ] Decide: commit or stash the 4 modified non-token files
- [ ] Commit the 3 new research docs (or keep as untracked during Phase 1)
- [ ] Ensure a clean `git status` before Phase 1 code changes

---

### R2: Accurately Measure Fixed Overhead Token Count

**Problem**: The current estimate of ~32,379 tokens for cacheable prefix is based on character counts ÷ 5. Real tokenization may differ by ±30%. SCLOR (M4) and CWAR estimation (M3) depend directly on this number.

**Resolution**: Run a calibration session against the Anthropic API to get actual token counts.

```python
# Calibration script to get exact token counts
import anthropic
client = anthropic.Anthropic()
# Count tokens for each component separately
components = {
    "CLAUDE.md": open("CLAUDE.md").read(),
    "skills": "...",  # concatenated skill frontmatter
    "agents": "...",  # concatenated agent frontmatter
}
for name, text in components.items():
    resp = client.messages.count_tokens(
        model="claude-sonnet-4-6",
        messages=[{"role": "user", "content": text}],
    )
    print(f"{name}: {resp.input_tokens} tokens")
```

**Alternative**: If Anthropic API access isn't available, use `tiktoken` or Claude's tokenizer to estimate.

**Action items**:
- [ ] Run token count calibration for CLAUDE.md, skills, agents, system tools
- [ ] Document the actual token counts in `config.yaml` under a new `overhead` section
- [ ] Update the `estimated_overhead_tokens` constant in metrics_engine.py

---

### R3: Workload Classification for Existing 29 Sessions

**Problem**: The workload classifier (Phase 3) needs per-category baselines for TLR, SCLOR, and STES normalization. Without backfilled workload tags on the existing 29 sessions, we'll have no calibration data for at least 2 weeks after deployment.

**Resolution**: Manually tag the existing 29 sessions by task type.

**Action items**:
- [ ] Query existing sessions: `python -m tools.token_audit db list --limit 50`
- [ ] Cross-reference with completed-task archives in `docs/completed-tasks/`
- [ ] Tag each session with `task_type` and `task_risk_level`
- [ ] Update the database: add a migration script that backfills these tags
- [ ] Compute initial per-workload baselines (TLR ranges, CPCT averages)

---

### R4: JSONL Encoding Handling

**Problem**: Direct file reads of JSONL transcripts fail with `UnicodeDecodeError: 'gbk' codec can't decode byte 0xae`. The current parser handles this (via `IncrementalJSONLParser`), but any new code that reads JSONL files directly will hit this.

**Resolution**: Ensure all JSONL reading goes through `IncrementalJSONLParser` which handles encoding. Document this constraint.

**Action items**:
- [ ] Verify `IncrementalJSONLParser` handles UTF-8 with fallback
- [ ] Add encoding note to `metrics_engine.py` docstring
- [ ] Never use bare `open(path)` for JSONL files — always use the parser

---

### R5: Provider-Aware Cache Field Mapping

**Problem**: Anthropic and DeepSeek report cache fields differently:

| Field | Anthropic | DeepSeek |
|-------|----------|----------|
| `cache_read_input_tokens` | Yes | Yes |
| `cache_creation_input_tokens` | Yes (non-zero on first write) | Yes (always 0) |
| `cache_creation.ephemeral_5m_input_tokens` | Sometimes | Always 0 |
| `cache_creation.ephemeral_1h_input_tokens` | Sometimes | Always 0 |

M2 and M3 formulas need to be provider-aware.

**Resolution**: Add a `provider` field to the session record. Use provider-specific estimation strategies.

```python
PROVIDER_CACHE_BEHAVIOR = {
    "deepseek-v4-pro": {
        "reports_cache_creation": False,
        "estimation_strategy": "fixed_prefix",
    },
    "deepseek-v4-flash": {
        "reports_cache_creation": False,
        "estimation_strategy": "fixed_prefix",
    },
    "claude-sonnet-4-6": {
        "reports_cache_creation": True,
        "estimation_strategy": "api_data",
    },
}
```

**Action items**:
- [ ] Add provider detection to session import
- [ ] Implement provider-aware cache field mapping in `metrics_engine.py`
- [ ] Test with at least one Anthropic session to validate the "api_data" path

---

## Preparation Checklist Summary

### Phase 0 Actions (Do Now)

| # | Item | Blocking? | Est. Time | Owner |
|---|------|-----------|-----------|-------|
| B1 | Investigate cache_creation data gap; implement estimation fallback | **YES** | 2h | gcs-token-audit-steward |
| B2 | Install pytest; create conftest.py + retroactive parser tests | **YES** | 1h | gcs-token-audit-steward |
| B3 | Backup audit.db; test migration on copy | **YES** | 30min | gcs-token-audit-steward |
| B4 | Create and validate task card | **YES** | 30min | gcs-token-audit-steward |
| R1 | Clean up dirty working tree (commit or stash unrelated changes) | No | 30min | User decision |
| R2 | Measure actual fixed overhead token counts | No | 1h | gcs-token-audit-steward |
| R3 | Backfill workload classification for 29 existing sessions | No | 1.5h | gcs-token-audit-steward |
| R4 | Document JSONL encoding constraint | No | 15min | gcs-token-audit-steward |
| R5 | Design provider-aware cache field mapping | No | 1h | gcs-token-audit-steward |

### Phase 0 Total: ~8 hours (blocking: ~4 hours)

### Dependency: B1 Must Be Resolved First

B1 (cache_creation data gap) determines the entire design of M2 and M3. All other items can be done in parallel. **B1 must be resolved before Phase 2 code can be finalized** (Phase 1 schema changes are unaffected).

### Recommended Order

1. B3 (backup DB) — 30 min, no dependencies
2. B4 (task card) — 30 min, no dependencies
3. B2 (pytest) — 1h, no dependencies
4. B1 (cache_creation investigation) — 2h, START FIRST due to research time
5. R1 (clean tree) — 30 min
6. R5 (provider mapping) — 1h, depends on B1 findings
7. R2 (token count) — 1h
8. R3 (backfill workloads) — 1.5h
9. R4 (encoding doc) — 15 min

---

## Go/No-Go Decision

After Phase 0 is complete, verify:

- [ ] `cache_creation_input_tokens` estimation strategy is documented and validated
- [ ] `python -m pytest tools/token_audit/tests/ -v` passes (at least 0 tests, no import errors)
- [ ] `audit.db.pre-v2-backup` exists and is identical to `audit.db`
- [ ] Migration test on copy succeeded with all 29 sessions intact
- [ ] Task card is created, validated, and linked
- [ ] Working tree is clean (only token-econ changes remain)
- [ ] Fixed overhead token counts are measured and documented in config
- [ ] Provider-aware cache mapping is designed

**If all items checked**: Proceed to Phase 1 (Schema Migration).

**If B1 cannot be resolved**: Revisit whether M2/M3 should use a simplified model, or defer cache health framework to a later phase.
