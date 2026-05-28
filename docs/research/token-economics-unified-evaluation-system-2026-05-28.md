# GCS Token Economic Benefit Evaluation System — Unified Metric Architecture

**Date**: 2026-05-28
**Status**: Design proposal
**Depends on**: [Multi-Paradigm Research Report](../docs/research/token-economics-multi-paradigm-analysis-2026-05-28.md)
**Audience**: GCS token-audit-steward, session-close-orchestrator, bookkeeper agents

---

## Executive Summary

This document defines a **unified, multi-layered token economic benefit evaluation system** for GCS. It synthesizes seven industry evaluation paradigms into a single coherent architecture with four layers: raw telemetry, derived metrics, composite indices, and decision rules. The system is designed to be implementable in Python with the existing GCS token audit infrastructure (`tools/token_audit/`).

The key innovation is that **cache hit rate is demoted from a standalone KPI to one input among many**, gated by staleness detection and workload context. No single number captures token economic health — the system reports a **metric vector** with workload-conditional interpretation.

---

## 1. Design Philosophy

### 1.1 First Principles

| Principle | Implication |
|-----------|-------------|
| **Value is multidimensional** | No single composite score; always report the vector |
| **Context determines interpretation** | The same metric means different things in different workload classes |
| **Cache is a means, not an end** | Cache metrics are always paired with staleness/freshness metrics |
| **Cost is measured against output, not input** | Efficiency = value delivered ÷ tokens consumed, not tokens saved ÷ tokens possible |
| **Risk is a first-class dimension** | Token savings that increase error risk are net-negative after risk adjustment |
| **Fixed costs must be amortized** | Per-session overhead is tracked separately and amortized over session length |
| **Metrics must be computable from available data** | Every metric maps to concrete fields in Claude Code usage responses and session transcripts |

### 1.2 What We Optimize For

The system optimizes for **risk-adjusted task completion efficiency** — maximizing the probability of successful task completion per unit of token cost, with explicit penalties for:

- Verification gaps (cutting verification tokens to save cost)
- Context staleness (serving outdated information)
- Cold-load overhead (paying fixed costs without amortization)
- Token waste (tokens that didn't influence the output)

---

## 2. Metric Architecture: Four-Layer Model

```
Layer 4: DECISION RULES ── Alert thresholds, optimization recommendations, trend alarms
     ▲
Layer 3: COMPOSITE INDICES ── Token Health Score, Cache Trust Index, Session Efficiency Rating
     ▲
Layer 2: DERIVED METRICS ── Cost-per-task, amortized overhead, USR, token leverage ratio
     ▲
Layer 1: RAW TELEMETRY ── Token counts, cache events, session duration, task outcome
```

### 2.1 Layer 1: Raw Telemetry

Data collected directly from API responses and session metadata. No computation — pure observation.

| Field | Source | Type | Description |
|-------|--------|------|-------------|
| `input_tokens` | API `usage` | int | Total input tokens (uncached + cached read + cache write) |
| `output_tokens` | API `usage` | int | Total output tokens generated |
| `cache_read_input_tokens` | API `usage` | int | Tokens served from cache |
| `cache_creation_input_tokens` | API `usage` | int | Tokens written to cache |
| `session_duration_seconds` | Session clock | float | Wall-clock session duration |
| `turn_count` | Message counter | int | Number of user + assistant turns |
| `tool_call_count` | Tool use counter | int | Number of tool invocations |
| `task_outcome` | Task card status | enum | `completed` / `partial` / `failed` / `abandoned` |
| `task_type` | Task card scope | enum | `bug-fix` / `feature` / `refactor` / `research` / `docs` / `ops` |
| `task_risk_level` | Task card risk | enum | `low` / `medium` / `high` / `critical` |
| `model_id` | API metadata | string | Model identifier (e.g., `claude-sonnet-4-6`) |
| `cache_ttl_setting` | API request | enum | `5min` / `1hour` / `none` |
| `session_id` | Session metadata | string | Unique session identifier |

### 2.2 Layer 2: Derived Metrics

Computed from Layer 1 data. These are the building blocks for composite indices.

#### M1: Cache Hit Rate (Standard)

$$HR = \frac{cache\_read\_input\_tokens}{cache\_read\_input\_tokens + cache\_creation\_input\_tokens}$$

- **Range**: 0–1
- **Interpretation**: Fraction of cacheable tokens served from cache rather than recomputed
- **Blind spot**: Does not measure staleness, bloat, or write-premium economics
- **Use**: Baseline only; never reported alone

#### M2: Effective Cache Hit Rate (Write-Premium Adjusted)

$$HR_{eff} = \frac{cache\_read\_input\_tokens \times 0.10}{cache\_creation\_input\_tokens \times w + cache\_read\_input\_tokens \times 0.10 + uncached\_input\_tokens \times 1.0}$$

Where $w$ is the write premium: 1.25 for 5-min TTL, 2.0 for 1-hour TTL.

- **Range**: 0–1
- **Interpretation**: Cost-adjusted cache efficiency — how much you actually saved relative to the uncached baseline cost
- **Key difference from M1**: A session with many cache writes and few reads scores lower on M2 than M1, because the write premium is priced in
- **Use**: Primary cache efficiency metric; replaces raw HR in dashboards

#### M3: Cache Write Amortization Ratio

$$CWAR = \frac{cache\_read\_input\_tokens}{cache\_creation\_input\_tokens}$$

- **Range**: 0–∞
- **Interpretation**: How many times each cached token was read, on average
- **Break-even thresholds**:
  - 5-min TTL: CWAR ≥ 1.4 is net-positive
  - 1-hour TTL: CWAR ≥ 2.2 is net-positive
- **Red flag**: CWAR < 1.0 means you're paying more to write than you save from reading
- **Use**: Early warning for TTL mismatch or traffic pattern problems

#### M4: Session Cold-Load Overhead Ratio

$$SCLOR = \frac{estimated\_fixed\_overhead\_tokens}{total\_input\_tokens}$$

Where `estimated_fixed_overhead_tokens` is the sum of tokens from skill/agent frontmatter, CLAUDE.md, tool definitions, and memory files loaded at session start.

- **Range**: 0–1
- **Interpretation**: What fraction of input tokens is infrastructure overhead rather than task work
- **Healthy range**: <5% for sessions >50 turns; <15% for sessions <10 turns
- **Use**: Tracks whether fixed costs are proportional to session value

#### M5: Cold-Load Amortization Efficiency

$$CLAE = \frac{task\_work\_tokens}{fixed\_overhead\_tokens \times session\_count\_rolling\_7d}$$

Where `task_work_tokens = total_input_tokens - estimated_fixed_overhead_tokens`.

- **Range**: 0–∞
- **Interpretation**: How many tokens of task work each token of fixed overhead "buys"
- **Use**: Justifies (or questions) the size of skill/agent definitions

#### M6: Token Leverage Ratio (Output/Input Efficiency)

$$TLR = \frac{output\_tokens}{input\_tokens}$$

- **Range**: 0–∞ (typically 0.01–0.5)
- **Interpretation**: How many output tokens are produced per input token
- **Healthy range by workload**:
  - Code generation: 0.05–0.20
  - Architecture design: 0.02–0.10
  - Research/exploration: 0.01–0.05
  - Bug investigation: 0.02–0.08
- **Red flag**: TLR < 0.01 across multiple sessions → likely context bloat or excessive tool definitions
- **Use**: Coarse efficiency signal; must be workload-normalized

#### M7: Token Waste Ratio

$$TWR = \frac{estimated\_wasted\_tokens}{total\_input\_tokens}$$

Where wasted tokens are estimated as:
- Tokens in turns that were later reverted or abandoned
- Tokens from tool calls that returned errors and were retried identically
- Tokens from reading files that were not referenced in subsequent turns

- **Range**: 0–1
- **Interpretation**: Fraction of tokens that did not contribute to the final output
- **Use**: Identifies process inefficiency (repeated reads, error-retry loops)

#### M8: Unsafe-Served Rate Estimate (USR)

$$USR = \frac{sessions\_with\_stale\_context\_errors}{total\_sessions}$$

Where "stale context errors" are detected via:
1. Agent reads a file, file is edited externally, agent reads again and gets different content
2. Agent references a skill/agent definition that has been updated since session start
3. Agent acts on tool output that is >TTL old

- **Range**: 0–1
- **Interpretation**: Fraction of sessions where caching may have served stale information
- **Use**: The counterweight to cache hit rate — high HR + high USR = dangerous caching

#### M9: Session Token Efficiency Score (STES)

$$STES = \frac{task\_outcome\_value}{total\_tokens \times model\_cost\_per\_token}$$

Where `task_outcome_value` is:
- 1.0 for fully completed tasks
- 0.5 for partially completed tasks
- 0.15 for failed tasks (negative value of learning)
- 0.0 for abandoned tasks

- **Range**: 0–∞ (higher is better)
- **Interpretation**: Task value per dollar of token cost
- **Use**: Primary efficiency metric for cross-session comparison

#### M10: Cost-per-Completed-Task (by task type)

$$CPCT_{type} = \frac{\sum cost\_per\_session}{\sum completed\_tasks\_of\_type}$$

Computed per task type (bug-fix, feature, refactor, research, docs, ops).

- **Unit**: $/completed-task
- **Interpretation**: How much token cost a completed task of a given type typically requires
- **Use**: Trend analysis; budget planning; identifies task types with disproportionate token cost

#### M11: Verification Coverage Ratio

$$VCR = \frac{verification\_tokens}{action\_tokens}$$

Where:
- `verification_tokens` = tokens spent on test runs, lint checks, type checks, review steps
- `action_tokens` = tokens spent on code generation, file writes, edits

- **Range**: 0–∞ (typically 0.05–0.50)
- **Interpretation**: How much verification is done per unit of action
- **Healthy range by risk level**:
  - Low risk: 0.05–0.15
  - Medium risk: 0.10–0.25
  - High risk: 0.20–0.50
  - Critical risk: 0.30–0.80
- **Red flag**: VCR falling below the risk-appropriate range → cutting verification to save tokens
- **Use**: Directly implements the risk-adjustment dimension

#### M12: Context Growth Rate

$$CGR = \frac{input\_tokens\_turn\_N}{input\_tokens\_turn\_1}$$

Where N is the last turn of the session.

- **Range**: 1–∞ (typically 1–30)
- **Interpretation**: How much the context window grew during the session
- **Red flag**: CGR > 10 with TLR < 0.02 → context bloat without proportional output
- **Use**: Early warning for context accumulation pathology

#### M13: Tool Definition Overhead Ratio

$$TDOR = \frac{tool\_definition\_tokens}{total\_input\_tokens}$$

- **Range**: 0–1
- **Interpretation**: What fraction of input tokens is tool definitions
- **Red flag**: TDOR > 0.20 → tool definitions are dominating task content
- **Use**: Triggers tool pruning reviews

---

### 2.3 Layer 3: Composite Indices

Composite indices aggregate multiple derived metrics into interpretable scores. Each index has a defined formula, weight vector, and interpretation guide.

#### CI-1: Token Health Score (THS)

**Purpose**: Single-number session-level token economic health. Scored 0–100.

**Formula**:

$$THS = 100 \times (w_1 \cdot HR_{eff} + w_2 \cdot (1 - SCLOR) + w_3 \cdot TLR_{norm} + w_4 \cdot (1 - TWR))$$

Where:
- $HR_{eff}$ = Effective Cache Hit Rate (M2), already 0–1
- $SCLOR$ = Session Cold-Load Overhead Ratio (M4), 0–1
- $TLR_{norm}$ = Token Leverage Ratio (M6) normalized to 0–1 using workload-specific benchmarks
- $TWR$ = Token Waste Ratio (M7), 0–1

**Default weights** (tunable per workload):

| Weight | Value | Rationale |
|--------|-------|-----------|
| $w_1$ (cache) | 0.20 | Cache is important but not dominant |
| $w_2$ (overhead) | 0.25 | Fixed overhead directly wastes tokens every session |
| $w_3$ (leverage) | 0.30 | Output/input efficiency is the core productivity signal |
| $w_4$ (waste) | 0.25 | Waste directly measures process inefficiency |

**Interpretation**:

| THS Range | Label | Action |
|-----------|-------|--------|
| 80–100 | Healthy | No action; monitor trends |
| 60–79 | Adequate | Review overhead and waste metrics |
| 40–59 | Concerning | Investigate specific low sub-scores |
| 20–39 | Poor | Active optimization required |
| 0–19 | Critical | Structural problem; escalate |

**Important**: THS is a *session-level diagnostic*, not a goal. Optimizing directly for THS (Goodhart's law) leads to gaming. Use it to identify sessions that need human review, not to rank sessions.

#### CI-2: Cache Trust Index (CTI)

**Purpose**: Is our caching actually helping, or is it masking problems?

**Formula**:

$$CTI = HR_{eff} \times (1 - USR) \times min(1, CWAR / CWAR_{break\_even})$$

Where:
- $HR_{eff}$ = Effective Cache Hit Rate (M2)
- $USR$ = Unsafe-Served Rate (M8)
- $CWAR$ = Cache Write Amortization Ratio (M3)
- $CWAR_{break\_even}$ = 1.4 for 5-min TTL, 2.2 for 1-hour TTL

**Range**: 0–1

**Interpretation**:

| CTI Range | Label | Meaning |
|-----------|-------|---------|
| 0.80–1.00 | Trustworthy | Cache is saving money safely |
| 0.60–0.79 | Cautious | Cache is net-positive but monitor USR |
| 0.40–0.59 | Suspicious | Cache may be losing money or serving stale data |
| 0.20–0.39 | Untrustworthy | Cache is actively harmful — review immediately |
| 0.00–0.19 | Broken | Cache strategy needs fundamental redesign |

**Key property**: CTI penalizes high HR when USR is also high or when CWAR is below break-even. This directly addresses the "high cache hit rate is not necessarily good" problem.

#### CI-3: Session Efficiency Rating (SER)

**Purpose**: Multi-dimensional session quality score incorporating cost, outcome, and risk.

**Formula**:

$$SER = STES_{norm} \times VCR_{adequacy} \times (1 - \alpha \cdot USR)$$

Where:
- $STES_{norm}$ = Session Token Efficiency Score (M9) normalized to 0–1 against historical baseline
- $VCR_{adequacy}$ = min(1, VCR / VCR_target) — penalizes sessions below risk-appropriate verification
- $\alpha$ = staleness penalty weight (default 0.5)
- $USR$ = Unsafe-Served Rate (M8)

**Range**: 0–1

**Interpretation**:

| SER Range | Label | Description |
|-----------|-------|-------------|
| 0.80–1.00 | Excellent | Efficient, well-verified, trustworthy |
| 0.60–0.79 | Good | Minor efficiency or verification gaps |
| 0.40–0.59 | Fair | Multiple dimensions need improvement |
| 0.20–0.39 | Poor | Significant problems in ≥2 dimensions |
| 0.00–0.19 | Failing | Session should be reviewed for process failure |

#### CI-4: Aggregate Token Economic Index (ATEI)

**Purpose**: Rolling 7-day aggregate health of the entire GCS token economy. This is the "headline number" for trend dashboards.

**Formula**:

$$ATEI = \frac{1}{N} \sum_{i=1}^{N} SER_i \times w_{type}(task\_type_i)$$

Where $w_{type}$ adjusts for the inherent efficiency differences between task types:

| Task Type | Weight | Rationale |
|-----------|--------|-----------|
| bug-fix | 1.0 | Baseline |
| feature | 0.85 | Inherently more exploratory, expect lower SER |
| refactor | 0.90 | Moderate complexity |
| research | 0.70 | High token use is expected and valuable |
| docs | 0.95 | Should be efficient |
| ops | 0.90 | Routine operations should be streamlined |

**Range**: 0–1

**Interpretation**: Tracked as a time series. The absolute value matters less than the trend. A declining ATEI over 14+ days signals systemic degradation.

---

### 2.4 Layer 4: Decision Rules

Decision rules map metric states to concrete actions. They are designed to be automatable — the token audit tooling can flag sessions without human review.

#### Rule D1: Cache Deception Alert

**Condition**: `HR > 0.90 AND CTI < 0.50`

**Meaning**: Cache hit rate is excellent but the cache is probably losing money or serving stale data.

**Action**: Flag session for manual review. Check for:
- TTL mismatches (traffic gaps > TTL)
- Dynamic content inside cache breakpoints
- Stale file references

#### Rule D2: Context Bloat Alarm

**Condition**: `CGR > 10 AND TLR < 0.02`

**Meaning**: Context grew 10× during the session but output per input token is very low.

**Action**: Recommend context compaction or session restart. Flag for session design review.

#### Rule D3: Verification Gap Alert

**Condition**: `VCR < VCR_target * 0.5` (where VCR_target is risk-level-appropriate)

**Meaning**: Verification tokens are less than half the risk-appropriate level.

**Action**: Flag task for additional verification. In high/critical risk tasks, escalate to human review.

#### Rule D4: Cold-Load Dominance Alert

**Condition**: `SCLOR > 0.25 AND turn_count < 5`

**Meaning**: More than 25% of input tokens are fixed overhead, and the session was very short.

**Action**: Review whether the task justified a full agentic session. Consider whether the task could have been done in a simpler mode.

#### Rule D5: Write-Premium Loss Alert

**Condition**: `CWAR < 1.0` (any TTL) or `CWAR < 2.2` (1-hour TTL)

**Meaning**: Cache writes are not being read enough to justify the write premium.

**Action**: Consider reducing TTL (switch from 1-hour to 5-min) or disabling caching for this workload pattern.

#### Rule D6: ATEI Decline Alert

**Condition**: `ATEI_7d_average < ATEI_14d_average * 0.85`

**Meaning**: 7-day average ATEI has dropped more than 15% below the 14-day baseline.

**Action**: Trigger token audit review. Check for recent changes to skill/agent definitions, CLAUDE.md, tool configurations, or workload patterns.

#### Rule D7: Task Type Cost Anomaly

**Condition**: `CPCT_type > CPCT_type_historical * 1.5`

**Meaning**: A specific task type is costing 50% more than its historical average.

**Action**: Review recent sessions of that type for common inefficiency patterns.

---

## 3. Cache Health Framework

The cache health framework is the system's direct response to the "cache hit rate too high is not necessarily good" problem. It decomposes cache performance into three orthogonal dimensions:

### 3.1 The Three Dimensions of Cache Health

```
                    CACHE HEALTH
                         │
          ┌──────────────┼──────────────┐
          │              │              │
    EFFICIENCY      FRESHNESS      ECONOMICS
    (Is it fast?)   (Is it right?) (Is it worth it?)
          │              │              │
    HR_eff (M2)     USR (M8)       CWAR (M3)
    HR_raw (M1)     Stale refs     Write cost/read
    TTFT impact     File version   TTL match
```

**A healthy cache scores well on ALL THREE dimensions.** A cache with high efficiency but poor freshness is dangerous. A cache with high efficiency but poor economics is wasteful. Only when all three are green is the cache truly healthy.

### 3.2 Cache Health States

| State | Efficiency | Freshness | Economics | CTI Range | Interpretation |
|-------|-----------|-----------|-----------|-----------|----------------|
| **Ideal** | High | High | High | 0.80–1.00 | Cache is a net positive across all dimensions |
| **Wasteful** | High | High | Low | 0.50–0.79 | Cache works but costs more than it saves (TTL mismatch) |
| **Dangerous** | High | Low | High | 0.30–0.59 | Fast, cheap, but wrong — the worst state |
| **Inefficient** | Low | High | High | 0.40–0.69 | Cache is safe but not helping much |
| **Broken** | Low | Low | Low | 0.00–0.29 | Cache is actively harmful |

### 3.3 Cache Health Diagnostic Flowchart

```
Session Complete
       │
       ▼
  ┌─────────────┐
  │ Compute M1   │  Raw cache hit rate
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐     YES    ┌──────────────────────────┐
  │ M1 > 0.85?  │───────────▶│ WARNING: High hit rate   │
  └──────┬──────┘            │ Proceed with extra scrutiny│
         │ NO                └────────────┬─────────────┘
         │                               │
         ▼                               ▼
  ┌─────────────┐              ┌─────────────┐
  │ Compute M2   │              │ Compute M8   │  USR check
  │ HR_eff       │              │ Check staleness│
  └──────┬──────┘              └──────┬──────┘
         │                            │
         ▼                            ▼
  ┌─────────────┐              ┌─────────────┐
  │ Compute M3   │              │ USR > 0.05? │──YES──▶ DANGEROUS CACHE
  │ CWAR         │              └──────┬──────┘          (flag immediately)
  └──────┬──────┘                     │ NO
         │                            │
         ▼                            ▼
  ┌─────────────┐              ┌─────────────┐
  │CWAR < break?│──YES──▶ WASTEFUL           │
  │             │          CACHE              │
  │    NO       │          (TTL review)       │
  └──────┬──────┘                            │
         │                                   │
         ▼                                   ▼
  ┌─────────────┐              ┌─────────────┐
  │ Compute CTI  │◀─────────────│ All clear    │
  │ Cache Trust  │              │              │
  └──────┬──────┘              └──────┬──────┘
         │                            │
         ▼                            ▼
    Report CTI + State          IDEAL CACHE
```

---

## 4. Workload Classification

Different session types have fundamentally different token economics. The system classifies every session into a workload category and applies category-specific benchmarks.

### 4.1 Workload Categories

| Category | Typical Tasks | Expected TLR Range | Expected Session Length | Expected HR Range |
|----------|--------------|-------------------|------------------------|-------------------|
| **code-gen** | Feature implementation, bug fixes | 0.05–0.20 | 20–80 turns | 0.75–0.95 |
| **code-review** | PR review, diff analysis | 0.02–0.08 | 10–30 turns | 0.60–0.85 |
| **architecture** | Design docs, planning, refactor design | 0.02–0.10 | 15–60 turns | 0.70–0.90 |
| **research** | Literature review, technology evaluation | 0.01–0.05 | 20–100 turns | 0.50–0.80 |
| **debug** | Bug investigation, root cause analysis | 0.02–0.08 | 10–50 turns | 0.55–0.80 |
| **docs** | Documentation generation, updates | 0.03–0.12 | 10–40 turns | 0.65–0.85 |
| **ops** | CI fixes, build config, dependency updates | 0.04–0.15 | 5–25 turns | 0.70–0.90 |
| **process** | Session close, task management, audit | 0.01–0.05 | 5–20 turns | 0.80–0.95 |

### 4.2 Classification Logic

```python
def classify_workload(task_card, tool_call_pattern, output_content) -> WorkloadCategory:
    # Rule 1: Task card scope override
    if task_card.scope == "bug-fix":
        return WorkloadCategory.CODE_GEN if tool_use_ratio("Edit|Write") > 0.3 else WorkloadCategory.DEBUG
    if task_card.scope == "research":
        return WorkloadCategory.RESEARCH
    if task_card.scope == "docs":
        return WorkloadCategory.DOCS

    # Rule 2: Tool call pattern
    if tool_use_ratio("Read|Glob|Grep") > 0.6 and tool_use_ratio("Edit|Write") < 0.1:
        return WorkloadCategory.RESEARCH
    if tool_use_ratio("Bash.*test|Bash.*lint|Bash.*compile") > 0.15:
        return WorkloadCategory.OPS

    # Rule 3: Output content analysis
    if output_is_documentation(output_content):
        return WorkloadCategory.DOCS
    if output_is_architecture_plan(output_content):
        return WorkloadCategory.ARCHITECTURE

    return WorkloadCategory.CODE_GEN  # default
```

### 4.3 Category-Specific Thresholds

Each derived metric has category-specific healthy ranges. The composite indices use these ranges for normalization.

See Appendix A for the full threshold matrix.

---

## 5. Dashboard Design

### 5.1 Session-Level Diagnostic Card

Displayed at the end of each session (e.g., in the session-close-orchestrator output):

```
┌─────────────────────────────────────────────────────────┐
│ SESSION TOKEN ECONOMIC DIAGNOSTIC                        │
│ Session: 2026-05-28-token-audit-design                   │
│ Workload: architecture   Risk: medium   Model: sonnet-4.6│
├─────────────────────────────────────────────────────────┤
│                                                         │
│  TOKEN HEALTH SCORE:  78/100  ═══════════░░  ADEQUATE   │
│  CACHE TRUST INDEX:   0.87    ════════════░  TRUSTWORTHY│
│  SESSION EFF. RATING: 0.72    ═══════════░░  GOOD       │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  CACHE HEALTH                                           │
│  ┌──────────┬──────────┬──────────┐                     │
│  │EFFICIENCY│FRESHNESS │ECONOMICS │                     │
│  │  0.91 ▲  │  0.98 ▲  │  0.65 ▼  │                     │
│  │  (M2)    │  (1-USR) │  (CWAR)  │                     │
│  └──────────┴──────────┴──────────┘                     │
│  State: WASTEFUL — CWAR=1.1 below 5-min break-even (1.4)│
│  Fix: Consider 1-hour TTL or session batching            │
├─────────────────────────────────────────────────────────┤
│  KEY METRICS                                            │
│  Input tokens:     48,230    Output tokens:    3,845    │
│  TLR:              0.080     CGR:              3.2      │
│  SCLOR:            0.12      TWR (est):        0.08     │
│  VCR:              0.18      VCR target:       0.10-0.25│
│  Cold-load tokens: ~5,800    Amortized over:   8 turns  │
├─────────────────────────────────────────────────────────┤
│  ALERTS                                                 │
│  ⚠ CWAR below break-even — write premium loss           │
│  ✓ All other metrics within healthy range               │
└─────────────────────────────────────────────────────────┘
```

### 5.2 Rolling Trend Dashboard

For the 7-day and 30-day view:

```
┌─────────────────────────────────────────────────────────┐
│ GCS TOKEN ECONOMY — 7-DAY TREND                         │
│ May 21 – May 28, 2026     Sessions: 14   Tasks: 11      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ATEI (7d):  0.74  ▁▃▅▇▆▄▅  TREND: → STABLE            │
│  ATEI (30d): 0.71  ▂▃▄▅▅▆▆  TREND: ▲ IMPROVING         │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  BY WORKLOAD (7d)                                       │
│  code-gen:    0.78 ▲  (4 sessions, avg THS: 81)         │
│  research:    0.62 →  (3 sessions, avg THS: 65)         │
│  architecture:0.71 ▼  (2 sessions, avg THS: 73)         │
│  docs:        0.85 ▲  (2 sessions, avg THS: 88)         │
│  process:     0.69 →  (3 sessions, avg THS: 71)         │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  CACHE HEALTH TREND                                     │
│  CTI (7d avg): 0.83 →                                    │
│  USR (7d):     0.01 ✓  (0 stale context events)          │
│  CWAR (7d):    2.1  ✓  (above break-even)                │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  COST TREND                                             │
│  Total cost (7d):    $1.28                               │
│  Avg cost/session:   $0.091                              │
│  Avg cost/task:      $0.116                              │
│  CPCT (code-gen):    $0.08  (▼ 12% from 14d avg)        │
│  CPCT (research):    $0.15  (▲ 8% from 14d avg)         │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  ACTIVE ALERTS                                          │
│  None                                                   │
└─────────────────────────────────────────────────────────┘
```

---

## 6. Implementation Roadmap

### 6.1 Phase 1: Core Metrics (Week 1–2)

Implement Layer 1 and Layer 2 in `tools/token_audit/`:

**New module**: `tools/token_audit/metrics_engine.py`

```python
@dataclass
class RawTelemetry:
    input_tokens: int
    output_tokens: int
    cache_read_input_tokens: int
    cache_creation_input_tokens: int
    session_duration_seconds: float
    turn_count: int
    tool_call_count: int
    task_outcome: str
    task_type: str
    task_risk_level: str
    model_id: str
    cache_ttl_setting: str

@dataclass
class DerivedMetrics:
    hr_raw: float           # M1
    hr_effective: float     # M2
    cwar: float             # M3
    sclor: float            # M4
    clae: float             # M5
    tlr: float              # M6
    twr: float              # M7
    usr: float              # M8
    stes: float             # M9
    cpct: float             # M10
    vcr: float              # M11
    cgr: float              # M12
    tdor: float             # M13

def compute_derived_metrics(telemetry: RawTelemetry, historical_baselines: dict) -> DerivedMetrics:
    ...
```

**Integration point**: Call `compute_derived_metrics()` from `session-close-orchestrator` and append results to the session's completed-task report.

### 6.2 Phase 2: Composite Indices (Week 2–3)

**New module**: `tools/token_audit/composite_indices.py`

```python
@dataclass
class CompositeIndices:
    ths: float     # CI-1: Token Health Score
    cti: float     # CI-2: Cache Trust Index
    ser: float     # CI-3: Session Efficiency Rating
    atei: float    # CI-4: Aggregate Token Economic Index (computed across sessions)

def compute_composite_indices(metrics: DerivedMetrics, workload: str) -> CompositeIndices:
    ...

def compute_atei(sessions: list[CompositeIndices], task_types: list[str]) -> float:
    ...
```

**Integration point**: `session-close-orchestrator` prints the diagnostic card; `gcs-token-audit-steward` computes ATEI weekly.

### 6.3 Phase 3: Decision Rules & Alerting (Week 3–4)

**New module**: `tools/token_audit/decision_engine.py`

```python
@dataclass
class Alert:
    rule_id: str
    severity: str  # INFO, WARNING, CRITICAL
    message: str
    session_id: str

def evaluate_rules(metrics: DerivedMetrics, indices: CompositeIndices) -> list[Alert]:
    ...
```

**Integration point**: Alerts are included in the session diagnostic card and aggregated in the trend dashboard.

### 6.4 Phase 4: Dashboard & Trend Analysis (Week 4–5)

**New module**: `tools/token_audit/dashboard.py`

- `render_session_diagnostic()` — the per-session card (text-based, for inclusion in completed-task reports)
- `render_trend_dashboard()` — 7-day and 30-day aggregate views
- `render_cache_health_report()` — focused cache health deep-dive

**Integration point**: Called by `gcs-token-audit-steward` on weekly audit runs.

### 6.5 Phase 5: Historical Baselines & Calibration (Week 5–6)

- Collect 30 days of metric data to establish per-workload baselines
- Calibrate TLR normalization ranges per workload category
- Calibrate CPCT baselines per task type
- Tune composite index weights based on correlation with task success

---

## 7. Data Storage Schema

### 7.1 Session Metrics Record

Stored alongside each completed-task report:

```json
{
  "session_id": "2026-05-28-token-audit-design",
  "timestamp": "2026-05-28T14:30:00Z",
  "workload_category": "architecture",
  "task_type": "design",
  "task_risk_level": "medium",
  "task_outcome": "completed",
  "model_id": "claude-sonnet-4-6",
  "raw_telemetry": {
    "input_tokens": 48230,
    "output_tokens": 3845,
    "cache_read_input_tokens": 31200,
    "cache_creation_input_tokens": 8500,
    "session_duration_seconds": 1245.0,
    "turn_count": 24,
    "tool_call_count": 47,
    "cache_ttl_setting": "5min"
  },
  "derived_metrics": {
    "hr_raw": 0.786,
    "hr_effective": 0.312,
    "cwar": 3.67,
    "sclor": 0.120,
    "clae": 7.33,
    "tlr": 0.080,
    "twr_estimate": 0.08,
    "usr_events": 0,
    "stes": 0.026,
    "vcr": 0.18,
    "cgr": 3.2,
    "tdor": 0.15
  },
  "composite_indices": {
    "ths": 78,
    "cti": 0.87,
    "ser": 0.72
  },
  "alerts": [
    {
      "rule_id": "D5",
      "severity": "WARNING",
      "message": "CWAR=1.1 below 5-min break-even (1.4)"
    }
  ]
}
```

### 7.2 Aggregate Trend Record

Stored at `docs/reports/token-economy-trends/YYYY-MM-DD.json`:

```json
{
  "date": "2026-05-28",
  "period": "7d",
  "session_count": 14,
  "task_count": 11,
  "atei": 0.74,
  "atei_30d": 0.71,
  "by_workload": {
    "code-gen": {"sessions": 4, "avg_ths": 81, "avg_ser": 0.78},
    "research": {"sessions": 3, "avg_ths": 65, "avg_ser": 0.62},
    "architecture": {"sessions": 2, "avg_ths": 73, "avg_ser": 0.71},
    "docs": {"sessions": 2, "avg_ths": 88, "avg_ser": 0.85},
    "process": {"sessions": 3, "avg_ths": 71, "avg_ser": 0.69}
  },
  "cache_health": {
    "cti_avg": 0.83,
    "usr_total": 0,
    "cwar_avg": 2.1
  },
  "costs": {
    "total_7d": 1.28,
    "avg_per_session": 0.091,
    "avg_per_task": 0.116
  },
  "alerts_active": []
}
```

---

## 8. Integration with Existing GCS Infrastructure

### 8.1 Touch Points

| Existing Component | Integration |
|-------------------|-------------|
| `gcs-token-audit-steward` skill | Primary consumer — runs weekly audit, renders trend dashboard |
| `session-close-orchestrator` skill | Produces per-session diagnostic card; appends metrics JSON to completed-task archive |
| `bookkeeper` agent | Consumes CPCT and ATEI for cost-benefit analysis |
| `bladesmith-quench-forge` agent | Consumes SCLOR and TWR to identify process improvements |
| `tools/token_audit/` | New modules: `metrics_engine.py`, `composite_indices.py`, `decision_engine.py`, `dashboard.py` |
| `tools/recent-summary.py` | Enhanced to include token economic metrics in activity digest |

### 8.2 Backward Compatibility

Existing metrics (BEI, raw token counts, cache hit rate) continue to be computed. The new system adds derived metrics and composite indices as a superset. No existing reports break.

---

## 9. Calibration Protocol

### 9.1 Initial Baselines (First 30 Days)

Since GCS currently has limited historical data for the new metrics, initial baselines are set from industry research and will be recalibrated after 30 days of collection:

| Metric | Initial Baseline | Source |
|--------|-----------------|--------|
| TLR (code-gen) | 0.05–0.20 | Industry benchmarks |
| TLR (research) | 0.01–0.05 | Industry benchmarks |
| HR_eff healthy min | 0.40 | Anthropic pricing model |
| CWAR break-even (5min) | 1.4 | Anthropic pricing model |
| CWAR break-even (1hr) | 2.2 | Anthropic pricing model |
| SCLOR healthy max | 0.15 | GCS infrastructure audit |
| VCR (medium risk) | 0.10–0.25 | Industry best practices |
| USR acceptable max | 0.05 | GroundedCache paper |

### 9.2 Recalibration Cadence

- **Monthly**: Update per-workload TLR and CPCT baselines
- **Quarterly**: Review composite index weights; adjust if correlation with task success weakens
- **On infrastructure change**: Recompute SCLOR after any change to skill/agent definitions

---

## 10. Limitations & Known Issues

1. **Token Waste Ratio (M7) is an estimate**. Distinguishing "wasted" from "exploratory" tokens requires semantic analysis of session transcripts. Initial implementation uses heuristics (retried tool calls, abandoned branches).

2. **Unsafe-Served Rate (M8) has low base rate**. Stale context events are rare in GCS's current workflow (primarily single-session, single-user). The metric becomes more important if GCS adopts multi-session parallel worktree workflows.

3. **Task outcome is self-reported**. The `task_outcome` field comes from the task card closure, which is set by the agent itself. There's a risk of over-claiming completion. The existing `gcs-quality-steward` verification gate partially mitigates this.

4. **Workload classification is heuristic**. Edge cases (research-heavy bug fixes, code-heavy architecture sessions) may be misclassified. The system should log classification confidence and flag low-confidence classifications for review.

5. **Composite index weights are subjective**. The default weights reflect a balanced prioritization of efficiency, safety, and cost. Different projects may legitimately prefer different weight vectors. The system should support configurable weights.

6. **Cold-load overhead estimation is approximate**. Token counts for skill/agent definitions are estimated at ~5 chars/token. Actual tokenization varies. A more accurate count would require running the actual tokenizer.

---

## Appendix A: Full Threshold Matrix by Workload

| Metric | code-gen | code-review | architecture | research | debug | docs | ops | process |
|--------|----------|-------------|-------------|----------|-------|------|-----|---------|
| **TLR healthy min** | 0.05 | 0.02 | 0.02 | 0.01 | 0.02 | 0.03 | 0.04 | 0.01 |
| **TLR healthy max** | 0.20 | 0.08 | 0.10 | 0.05 | 0.08 | 0.12 | 0.15 | 0.05 |
| **CGR red flag** | 8 | 6 | 10 | 15 | 8 | 8 | 6 | 5 |
| **SCLOR healthy max** | 0.12 | 0.15 | 0.15 | 0.20 | 0.15 | 0.12 | 0.10 | 0.10 |
| **TWR healthy max** | 0.10 | 0.08 | 0.15 | 0.25 | 0.20 | 0.08 | 0.10 | 0.05 |
| **VCR target (low risk)** | 0.05–0.15 | 0.03–0.10 | 0.05–0.15 | — | 0.05–0.15 | 0.03–0.08 | 0.05–0.15 | 0.03–0.08 |
| **VCR target (med risk)** | 0.10–0.25 | 0.08–0.20 | 0.10–0.25 | — | 0.10–0.25 | 0.08–0.20 | 0.10–0.25 | 0.08–0.20 |
| **VCR target (high risk)** | 0.20–0.50 | 0.15–0.40 | 0.20–0.50 | — | 0.20–0.50 | 0.15–0.40 | 0.20–0.50 | 0.15–0.40 |
| **STES healthy min** | 0.015 | 0.020 | 0.010 | 0.005 | 0.010 | 0.020 | 0.025 | 0.030 |

## Appendix B: Formula Quick Reference

| ID | Name | Formula | Range |
|----|------|---------|-------|
| M1 | Cache Hit Rate (raw) | reads / (reads + writes) | 0–1 |
| M2 | Effective Cache Hit Rate | (reads×0.10) / (writes×w + reads×0.10 + uncached×1.0) | 0–1 |
| M3 | Cache Write Amortization | reads / writes | 0–∞ |
| M4 | Session Cold-Load Overhead | fixed_overhead / total_input | 0–1 |
| M5 | Cold-Load Amortization Eff. | task_tokens / (fixed_overhead × session_count_7d) | 0–∞ |
| M6 | Token Leverage Ratio | output / input | 0–∞ |
| M7 | Token Waste Ratio | wasted / total_input | 0–1 |
| M8 | Unsafe-Served Rate | stale_sessions / total_sessions | 0–1 |
| M9 | Session Token Eff. Score | outcome_value / (total_tokens × price) | 0–∞ |
| M10 | Cost-per-Completed-Task | Σcost / Σcompleted_by_type | $/task |
| M11 | Verification Coverage | verification_tokens / action_tokens | 0–∞ |
| M12 | Context Growth Rate | input_turn_N / input_turn_1 | 1–∞ |
| M13 | Tool Definition Overhead | tool_def_tokens / total_input | 0–1 |
| CI-1 | Token Health Score | 100 × Σ(w × normalized_metrics) | 0–100 |
| CI-2 | Cache Trust Index | HR_eff × (1−USR) × min(1, CWAR/break_even) | 0–1 |
| CI-3 | Session Efficiency Rating | STES_norm × VCR_adequacy × (1−α×USR) | 0–1 |
| CI-4 | Aggregate Token Economic Index | avg(SER × workload_weight) over 7d | 0–1 |
