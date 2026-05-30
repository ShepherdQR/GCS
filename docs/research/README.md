# Research Index — Multi-Agent Orchestration

**Last updated:** 2026-05-29

Three interconnected research documents covering the full stack of multi-agent orchestration:
from capability limits through design principles to concrete implementation patterns.

---

## Document Map

```
docs/research/
  │
  ├── 100-agent-systems-capability-analysis.md     [SCOUTING]
  │   What: Google's 93-agent OS demo verified; Claude's 100-agent feasibility analyzed
  │   When to read: Understanding the upper bound — can we even do this?
  │   Key finding: 100 agents technically possible, practically infeasible;
  │                3-5 agent sweet spot from 7 academic papers
  │
  ├── orchestrator-design-principles.md            [PRINCIPLES]
  │   What: 13 evidence-based design principles extracted from papers + GCS audit
  │   When to read: Before designing any multi-agent system
  │   Key finding: Task-structure-first, 3-5 golden ratio, centralized verification
  │                mandatory, explicit dispatch over prose convention
  │
  ├── 3-5-agent-orchestration-patterns.md          [PATTERNS]
  │   What: 5 concrete orchestration patterns with architectures, results, failure modes
  │   When to read: When choosing an architecture for a specific task
  │   Key finding: Simple beats complex (Independent Ensemble, Sequential Pipeline
  │                dominate Pareto frontier); execution grounding is strongest signal
  │
  └── (this file)                                   [INDEX]
      Cross-reference map and reading guide
```

## Reading Paths

### Path A: "Can we do 100 agents?" → "What should we do instead?"
1. Start: `100-agent-systems-capability-analysis.md` — understand the ceiling
2. Then: `orchestrator-design-principles.md` — internalize the constraints
3. Finally: `3-5-agent-orchestration-patterns.md` — pick a pattern

### Path B: "I have a task. Which pattern?"
1. Start: `3-5-agent-orchestration-patterns.md` — the Design Decision Tree
2. Reference: `orchestrator-design-principles.md` — specific principles for the chosen pattern

### Path C: "I'm building an orchestrator skill."
1. Start: `orchestrator-design-principles.md` — the full 13 principles
2. Then: `.claude/skills/orchestrator/SKILL.md` — the portable implementation
3. Reference: `3-5-agent-orchestration-patterns.md` — architecture-specific guardrails

## Key Numbers at a Glance

| Metric | Value | Source |
|---|---|---|
| Multi-agent sweet spot | 3–5 agents | Kim et al. (2025) |
| Sequential task degradation (multi-agent) | −39% to −70% | Kim et al. (2025) |
| Parallel task improvement (multi-agent) | Up to +80.9% | Kim et al. (2025) |
| Error amplification (no verification) | 17.2× | Kim et al. (2025) |
| Error amplification (centralized verification) | 4.4× | Kim et al. (2025) |
| Production failure rate (multi-agent) | 41–87% | Nechepurenko & Shuvalov (2026) |
| Failures from coordination (not capability) | 79% | Nechepurenko & Shuvalov (2026) |
| 2 diverse agents ≥ 16 homogeneous | — | Yang et al. (2026) |
| Simple configurations dominate Pareto frontier | Independent Ensemble, Sequential Pipeline | Nechepurenko & Shuvalov (2026) |
| AgentForge (5-agent, execution-grounded) | 40.0% SWE-Bench Lite | Anonymous (2026) |
| PerfOrch (4-agent, profiled pipeline) | 97.19% HumanEval-X | Qi et al. (2025) |
| Anthropic Harness (4-agent, episodic memory) | 40% faster, 25% fewer errors | Anthropic (2026) |
| Software Factory (adversarial pairing) | 88% autonomous PRs | ZenML (2026) |
| Google 93-agent OS demo | 12h, 2.6B tokens, <$1,000 | Google I/O (2026) |

## Related Artifacts

| Artifact | Location |
|---|---|
| Portable orchestrator skill | `.claude/skills/orchestrator/SKILL.md` |
| GCS session-close-orchestrator (fixed pipeline) | `.claude/skills/session-close-orchestrator/SKILL.md` |
| GCS agent registry & scorecard | `docs/agentic/institutional-agent-registry-and-scorecard.md` |
| GCS E002 agent patterns report | `docs/agentic/experience/002-.../research/01-session-agent-patterns-report.md` |
| GCS infrastructure audit (multi-agent) | Agent audit performed 2026-05-29 |
