# Orchestrator Decision Audit

Status: active
Date: 2026-05-30
Source: `.claude/skills/orchestrator/SKILL.md` (Phase 4.4)

## Purpose

Track orchestrator architecture decisions, rollbacks, and task outcomes for
continuous improvement of the agent dispatching system. Each entry records:
what architecture was chosen, whether it succeeded, and what was learned.

## Decision Log

| Date | Task | Architecture | Workers | Outcome | Tokens Wasted | Lesson |
|------|------|-------------|---------|---------|---------------|--------|
| 2026-05-30 | — | — | — | — | 0 | Initial scaffold |

## Rollback History

| Date | Task | Original Arch | Rollback Reason | Tokens Wasted |
|------|------|--------------|-----------------|---------------|

## Blacklist

Task types that triggered 3+ rollbacks and should not use certain architectures:

| Task Type | Blacklisted Architecture | Reason | Date Added |
|-----------|-------------------------|--------|------------|

## Quality Metrics

| Metric | Current | Trend |
|--------|---------|-------|
| Architecture success rate | — | — |
| Average tokens per task | — | — |
| Rollback rate | — | — |
| Worker failure rate | — | — |

## Update Rule

Update after every orchestrator invocation that involves:
- Architecture selection (single agent, prompt chain, parallel workers)
- Rollback due to architecture failure
- New task type that requires a novel dispatch pattern
