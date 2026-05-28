# GCS Project — Token Efficiency Audit & Recommendations

**Date**: 2026-05-28
**Scope**: GCS project AI infrastructure token waste analysis with actionable recommendations
**Baseline**: 14 sessions, 2.4M tokens, 98.8% cache hit rate, $1.28 total cost (deepseek-v4-pro pricing)

---

## Executive Summary

The GCS project has built a sophisticated agentic SE infrastructure — 25 domain skills, 14 institutional agents, token audit tooling, and 200 agentic docs. However, this infrastructure itself has become a **controllable token overhead of ~5,800 tokens per fresh session** (~8,800 including README indexes) — loaded upfront regardless of whether the session needs a C++ solver skill or a benchmark scout agent. At 14 sessions totaling 2.4M tokens (~171K avg), the overhead from skill/agent definitions alone represents **~5% of total token spend** — and this percentage grows as sessions become more frequent and shorter. The cache hit rate of 98.8% is excellent, but this masks the cost of the first cold-load per session. This report identifies 12 specific optimization opportunities with estimated savings of **30–50% on controllable token overhead**.

---

## 1. Current State: GCS AI Infrastructure Audit

### 1.1 Token Load Breakdown (Estimated, per Fresh Session)

| Component | Count | Est. Tokens | Controllable? |
|-----------|-------|-------------|---------------|
| System tools (built-in) | ~50 | ~20,400 | No |
| MCP tools (browser, preview, sessions) | ~15 | ~9,100 | Partially |
| **CLAUDE.md** | 1 file, 100 lines | ~780 | **Yes** |
| **Skill definitions (frontmatter)** | 25 skills | ~2,500 | **Yes** |
| **Agent definitions (frontmatter)** | 14 agents | ~1,400 | **Yes** |
| **skills/README.md** | 1 file | ~600 | **Yes** |
| **agents/README.md** | 1 file | ~600 | **Yes** |
| **Memory (MEMORY.md)** | 0 files | 0 | **Yes** (missing) |
| **.claude/current-task** | 1 file | Variable | **Yes** |
| **Controllable subtotal** | | **~5,880** | |
| **Total estimated startup** | | **~35,400** | |

> Note: Token counts are estimates at ~5 chars/token. Skill/agent descriptions (~100 chars each) are the frontmatter `description` field that Claude Code auto-loads for skill matching. The full SKILL.md bodies only load on invocation.

### 1.2 Asset Inventory

#### Skills (25 total, ~78KB)

| Category | Count | Total Size | Avg Size |
|----------|-------|------------|----------|
| Solver core | 8 | ~20KB | 2.5KB |
| Boundary/integration | 6 | ~18KB | 3.0KB |
| Quality/governance | 6 | ~18KB | 3.0KB |
| Audit/demo | 3 | ~11KB | 3.7KB |
| **Process (close, orchestrator)** | 2 | **~16.6KB** | **8.3KB** |

**Largest skills:**
- `session-close-orchestrator`: 10,801 bytes (~2,160 tokens) — **4× larger than average**
- `task-scoped-session-closer`: 5,752 bytes (~1,150 tokens)
- `gcs-repository-audit-steward`: 4,057 bytes (~810 tokens)
- `gcs-token-audit-steward`: 3,960 bytes (~790 tokens)

#### Agents (14 total, ~37KB)

| Maturity | Count | Total Size |
|----------|-------|------------|
| Practiced | 2 | ~7.1KB |
| Seed | 2 | ~5.3KB |
| Candidate | 9 | ~22KB |
| README | 1 | ~3.0KB |

#### docs/agentic/ (200 files, 1.4MB)

This is the largest contextual payload in the project. While not loaded into every session, it is frequently traversed by agents during task closure, experience extraction, and governance checks.

### 1.3 What's Working Well

| Strength | Detail |
|----------|--------|
| **Cache hit rate 98.8%** | Exceptional — well above the 40–70% community benchmark |
| **CLAUDE.md is lean** | 100 lines, 3.9KB — within the <2KB community target, well-structured |
| **Token audit active** | Stop hook captures session data; trend reports available |
| **Skills use progressive disclosure** | Body only loads on invocation; frontmatter descriptions are the overhead |
| **Git worktree convention** | Documented and used for parallel session isolation |

---

## 2. Issues & Recommendations

### Issue 1: 25 Skills + 14 Agents Load Descriptions Into Every Context

**Severity**: High | **Estimated savings**: 2,000–3,000 tokens/session

Every skill and agent has a `description` field in its frontmatter. Claude Code loads all of these to match against user intent. With 39 total (25 skills + 14 agents), that's ~3,900 tokens of description text loaded upfront.

**Recommendation A: Trim descriptions to ≤100 characters.**

Current descriptions average 150–250 characters. Target format: `[domain] — [trigger keywords]. [when to invoke].` under 100 chars.

Example before/after:
```
Before (180 chars): "Cross-module architecture steward for GCS. Invoke when changing architecture docs,
planning or reviewing cross-module refactors, naming target modules, deciding dependency direction,
mapping current code to target vocabulary..."

After (98 chars): "GCS cross-module architecture. Invoke for architecture docs, cross-module refactors,
dependency direction, or module naming."
```

Estimated savings: 25 skills × 80 chars + 14 agents × 60 chars = ~2,840 chars ≈ **570 tokens/session**.

**Recommendation B: Mark candidate agents as `agent-mode: manual`.**

The 9 candidate agents (governance-sentinel, demo-producer, benchmark-scout, release-shepherd, night-watch, acceptance-officer, collation-officer, bookkeeper, gardener) are rarely invoked. If Claude Code supports disabling auto-load for specific agents, they should only load when explicitly called. This saves ~900 tokens.

**Combined savings: ~1,500 tokens/session**.

---

### Issue 2: session-close-orchestrator SKILL.md Is 10.8KB

**Severity**: Medium | **Estimated savings**: 1,500 tokens on invocation

At 10,801 bytes, this is 4× the average skill size. When invoked (every session close), its full body loads into context. Much of this content is procedural — step sequences, template references — that could be compressed or split.

**Recommendation: Split into orchestrator (thin) + reference docs.**

The SKILL.md should be a thin dispatcher (~2KB) that:
1. Lists the 5 steps with 1-line descriptions
2. References external docs for detailed procedures
3. Delegates to sub-skills (task-scoped-session-closer, bladesmith-quench-forge, bookkeeper, gcs-token-audit-steward)

Move detailed procedures to `docs/agentic/session-close-procedures.md`.

Estimated savings: ~1,500 tokens per session close (every session).

---

### Issue 3: Memory System Is Completely Empty

**Severity**: High | **Estimated savings**: 500–2,000 tokens/session (avoidance of re-discovery)

The project memory directory (`~/.claude/projects/C--Codes-AI-GCS-A/memory/`) is empty — no MEMORY.md, no memory files. This means:

- Every session re-discovers user preferences from scratch
- Known gotchas and "NEVER do X" rules are only in CLAUDE.md
- Cross-session learning is lost
- The model has no persistent knowledge of what worked/failed before

Community research shows lost critical context after compacting wastes ~80K tokens per repeat mistake.

**Recommendation A: Create a minimal MEMORY.md index.**

Start with 3–4 entries and grow organically. Template:

```markdown
- [User Preferences](user-preferences.md) — language, style, and workflow preferences
- [Project Context](project-context.md) — current phase, active initiatives, deadlines
- [Known Gotchas](known-gotchas.md) — build issues, test quirks, dependency pitfalls
- [Feedback Log](feedback-log.md) — corrections and confirmations from user
```

**Recommendation B: Populate after next 2–3 sessions.**

Use bladesmith-quench-forge (already a Practiced agent) to extract durable lessons from recent session transcripts into memory files. The ~14MB of session transcripts contain substantial reusable knowledge currently going unused.

**Recommendation C: Set a Stop hook to remind about memory updates.**

Add to settings.json Stop hooks:
```json
{
  "type": "command",
  "command": "echo '[REMINDER] Update project memory if this session produced durable lessons'"
}
```

---

### Issue 4: No .claudeignore File

**Severity**: Medium | **Estimated savings**: Variable (can be 80%+ on search context)

Without `.claudeignore`, Claude Code tools (Glob, Grep, Read) traverse everything including `node_modules/` (if present), build artifacts, large binary files, and session transcripts.

**Recommendation: Create `.claudeignore`:**

```
# Build artifacts
out/
build/
*.exe
*.dll
*.obj
*.o
*.a
*.lib
*.pdb

# Python cache
__pycache__/
*.pyc
*.pyo
.venv/
venv/

# Large data
*.jsonl
*.bin
*.dat
*.zip
*.tar.gz

# Session transcripts (in home dir, but exclude from search)
~/.claude/projects/

# IDE files
.idea/
.vscode/
*.sln
*.vcxproj
```

This prevents agents from accidentally reading 2.7MB session transcript JSONL files during code exploration.

---

### Issue 5: No Model Routing Strategy

**Severity**: Medium | **Estimated savings**: 30–50% on sub-agent tasks

The project uses Claude Code's default model (Sonnet) for all work. Research shows 60–70% of agent tasks (file search, simple summaries, boilerplate) can use Haiku at ~1/20 the cost.

**Recommendation: Configure model routing for sub-agents.**

In Claude Code, specify model per sub-agent:

| Task Type | Model | Est. Cost/Task |
|-----------|-------|----------------|
| File exploration, grep, simple lookups | Haiku | $0.01–0.03 |
| Code generation, refactoring | Sonnet | $0.15–0.30 |
| Architecture decisions, critical validation | Opus | $0.50–1.50 |

Key targets for Haiku routing:
- **Explore agent**: Always use Haiku — it's read-only search
- **gardener**: Small fixes and maintenance
- **collation-officer**: Cross-reading docs for consistency
- **bookkeeper**: Token/cost tracking (deterministic work)

Estimated savings: ~30% on sub-agent token costs.

---

### Issue 6: skills/README.md and agents/README.md Duplicate Frontmatter Information

**Severity**: Low | **Estimated savings**: ~1,200 tokens/session

Both README files (~600 tokens each) summarize what's already in the skill/agent frontmatter descriptions. They provide human-facing indices but the AI already has this information from the descriptions.

**Recommendation: Consolidate into ultra-compact indexes (~100 tokens each).**

Replace the current README files with minimal keyword-to-skill mappings:

```markdown
# Skills Index
- architecture,cross-module,refactor,dependency → gcs-architecture-steward
- kernel,snapshot,state-delta,stable-id → gcs-kernel-contract-steward
- constraint,residual,jacobian,degeneracy → gcs-constraint-semantics-steward
- ...
```

This preserves machine-readable routing while cutting ~1,000 tokens. The full human-readable tables can move to `docs/agentic/skill-catalog.md`.

---

### Issue 7: 200 Files in docs/agentic/ (1.4MB)

**Severity**: Medium | **Estimated savings**: Reduction in exploration overhead

While not loaded into every context, agents frequently traverse this directory during task closure, experience extraction, and governance checks. 200 files with deep nesting create significant exploration overhead.

**Recommendation A: Periodic archival of inactive experience records.**

Many files under `docs/agentic/experience/` and `docs/agentic/institutional-agents/` are historical records (forging notes from specific dates, calibration logs). After 30 days without reference, move to `docs/archive/`.

**Recommendation B: Add `docs/agentic/` to agent path whitelists only when needed.**

In CLAUDE.md, specify that agentic docs should be read on-demand, not explored by default. Add a one-line pointer:
```
Agentic operating docs: docs/agentic/ (load specific files on demand, not by default)
```

---

### Issue 8: Sub-Agent Context Inheritance Not Configured

**Severity**: Medium | **Estimated savings**: 40%+ on sub-agent tasks

The Claude Code lazy-loading proposal (GitHub #19105) estimates that sub-agents with full context inheritance burn ~8K unnecessary tokens each. If the GCS project uses 3 sub-agents per session, that's ~24K tokens of duplicated context.

**Recommendation: Use minimal context inheritance for sub-agents.**

When spawning agents, pass only what's needed:
- **Explore agent**: Target directory + search query (not full CLAUDE.md)
- **Code review agent**: Diff + relevant file (not full project context)
- **Task close agent**: Task card + session summary (not full skill list)

This aligns with the research finding that sub-agents with isolated context save 40%+ on input tokens.

---

### Issue 9: Token Audit Database Has 0 Turns/Tool Calls Logged

**Severity**: Low | **Estimated savings**: Better visibility → better optimization

The token audit DB shows 14 sessions but 0 turns and 0 tool calls. This means per-turn and per-tool-call cost breakdown is unavailable — you can see total cost but not *where* tokens went.

**Recommendation: Investigate turn-level tracking.**

If the token audit tool supports finer granularity (per-turn, per-agent, per-tool-call), enable it. Knowing that Explore agents consume 40% of tokens vs. Edit operations consuming 15% enables targeted optimization.

---

### Issue 10: No Token Budget Governance

**Severity**: Low | **Estimated savings**: Preventative (avoids cost spikes)

The project has no per-session or per-task token budget. The community-documented worst case (887K tokens/min, $8,000–$15,000/session) happened because no budget guardrail existed.

**Recommendation: Set soft budgets per task type.**

| Task Type | Soft Budget | Hard Limit |
|-----------|------------|------------|
| Typo fix, documentation update | 50K tokens | 100K tokens |
| Single-file feature | 150K tokens | 300K tokens |
| Multi-module refactor | 500K tokens | 1M tokens |
| Exploratory research | 300K tokens | 500K tokens |

The token audit tool already has `watch` functionality — configure alerts at 80% of hard limit.

---

### Issue 11: Stop Hook Runs Python Import Every Session Close

**Severity**: Low | **Estimated savings**: 1–2s latency per close

The Stop hook runs `python -m tools.token_audit db import --project GCS-A` on every session close. This loads the full Python toolchain and processes JSONL transcripts. For short sessions, the hook overhead may exceed the session's actual work time.

**Recommendation: Make the hook async or add a size threshold.**

Skip import for sessions with <10K total tokens (likely chat-only or status checks). Only run the full import for non-trivial sessions.

---

### Issue 12: CLAUDE.md Could Be More Cache-Friendly

**Severity**: Low | **Estimated savings**: Marginal (cache structure optimization)

CLAUDE.md is already good at 100 lines. However, the "Key Architecture Docs" table and "Skill Invocation" table contain information partially duplicated in skill descriptions. Consider whether these tables provide unique value beyond what the skill/agent frontmatter already communicates.

**Recommendation: Keep CLAUDE.md as-is for now.**

At 100 lines / 3.9KB, it's within the community-recommended <2KB target. Only trim if it grows beyond 120 lines. The current structure is well-balanced.

---

## 3. Prioritized Action Plan

| Priority | Issue | Action | Effort | Savings |
|----------|-------|--------|--------|---------|
| **P1** | Empty memory system | Create MEMORY.md + 3–4 memory files | 30 min | Avoidance of re-discovery (up to 80K/mistake) |
| **P1** | 25 skills + 14 agents in context | Trim descriptions to ≤100 chars | 60 min | ~1,500 tokens/session |
| **P2** | No .claudeignore | Create .claudeignore | 10 min | Prevents accidental large-file reads |
| **P2** | session-close-orchestrator 10.8KB | Split into thin dispatcher + ref docs | 45 min | ~1,500 tokens/close |
| **P2** | Sub-agent context inheritance | Configure minimal inheritance | 30 min | 40%+ on sub-agent tasks |
| **P3** | README files duplicate frontmatter | Consolidate to keyword indexes | 20 min | ~1,000 tokens/session |
| **P3** | No model routing strategy | Configure Haiku for exploration agents | 30 min | ~30% on sub-agent costs |
| **P4** | Token audit lacks turn-level data | Investigate finer granularity | 60 min | Better optimization targeting |
| **P4** | No token budgets | Set soft budgets per task type | 20 min | Prevents cost spikes |
| **P5** | 200 files in docs/agentic/ | Archive inactive records | 2 hours | Reduced exploration overhead |
| **P5** | Stop hook runs every close | Add size threshold | 15 min | Marginal latency |
| **—** | CLAUDE.md audit | Keep as-is, monitor growth | 0 min | Already optimal |

---

## 4. Estimated Cumulative Savings

| Scenario | Current | After P1–P2 | After All |
|----------|---------|-------------|-----------|
| Controllable tokens per fresh session | ~5,880 | ~3,000 (−49%) | ~2,000 (−66%) |
| Session close orchestrator invocation | ~2,160 | ~600 (−72%) | ~600 (−72%) |
| Sub-agent task (exploration) | ~40,000 | ~15,000 (−62%) | ~10,000 (−75%) |
| Total tokens per typical session | ~171,000 | ~140,000 (−18%) | ~125,000 (−27%) |

*Typical session based on 14-session average of 171K tokens.*

---

## 5. Implementation Notes

### 5.1 Risk: Over-Optimization

The GCS project is a sophisticated agentic SE system — some token overhead is **necessary infrastructure**. The goal is not to minimize tokens at all costs, but to ensure each token in context provides **unique, non-discoverable value**. The "semantic density" principle applies: eliminate zero-information tokens, preserve high-signal ones.

### 5.2 Risk: Breaking Skill Auto-Invocation

Trimming skill descriptions too aggressively could break Claude Code's auto-invocation matching. Test after changes: invoke a task that should trigger a skill and verify it still matches.

### 5.3 Measurement

After implementing P1–P2 items, compare token audit reports over 5+ sessions to quantify actual savings vs. estimates.

---

## References

- [Token Efficiency Industry Report](token-efficiency-industry-report-2026-05-28.md) — companion research report
- [Claude Code Lazy-Loading Architecture (#19105)](https://github.com/anthropics/claude-code/issues/19105)
- [7 Critical Token-Wasting Patterns (#13579)](https://github.com/anthropics/claude-code/issues/13579)
- [GCS Token Audit Steward](../../.claude/skills/gcs-token-audit-steward/SKILL.md)
- [GCS Agentic Organization Map](../../docs/agentic/agentic-organization-operating-map.md)
