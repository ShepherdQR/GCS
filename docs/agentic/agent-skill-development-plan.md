# Agent & Skill Development Plan

Status: active
Date: 2026-05-28
Source: [agent-skill-asset-inventory.md](agent-skill-asset-inventory.md) key findings

## Purpose

Execute the highest-priority, self-contained work from the asset inventory
analysis. This plan covers work that can be completed now (skill/agent creation,
promotion, cleanup). Work that requires accumulated evidence over multiple
sessions (institutional agent promotion, governance eval advancement) is
deferred.

## Work Items

### Batch 1 — Immediate (this session)

| # | Item | Type | Rationale |
| --- | --- | --- | --- |
| P1 | Promote git-session-branch-steward | Skill + Agent promotion | Prototype exists in experience/003; prevents most common governance failure |
| P2 | Create gcs-benchmark-steward | New skill | Architecture plan exists; benchmark-scout agent has no skill counterpart |
| P3 | Clean up redundant candidate roles | Maintenance | 3 roles overlap with platform features or existing agents |
| P4 | Advance acceptance-officer toward seed | Agent advancement | Gate template + refusal eval are the only missing pieces |
| P5 | Update all indexes | Maintenance | Ensure README files and registry reflect new state |

### Batch 2 — Next session (requires evidence accumulation)

| # | Item | Type | Prerequisite |
| --- | --- | --- | --- |
| N1 | Night-Watch first calibration run | Agent advancement | Run full nightly pipeline; create findings artifacts |
| N2 | I003 Atelier Steward → Practiced | Agent promotion | 2 more real convention-fit reviews on rendered UI |
| N3 | I004 Art Director → Practiced | Agent promotion | 1-2 more visual reviews on rendered surfaces |
| N4 | Governance evals E-GOV-001, E-GOV-003 → L3 | Eval advancement | Validator implementation |

### Batch 3 — Future (plan-dependent)

| # | Item | Type | Prerequisite |
| --- | --- | --- | --- |
| F1 | gcs-release-steward skill | New skill | release-shepherd agent reaches seed |
| F2 | gcs-ci-operations-steward skill | New skill | CI friction becomes recurring |
| F3 | Evaluator-Calibrator agent | New agent | Governance evals reach L3+ |
| F4 | Postmortem Analyst agent | New agent | First real regression or near-miss |

## Execution Sequence (This Session)

```
Step 0: Write this plan document
Step 1: Promote git-session-branch-steward skill → .claude/skills/
Step 2: Promote git-session-steward agent → .claude/agents/
Step 3: Create gcs-benchmark-steward skill → .claude/skills/
Step 4: Clean redundant candidate roles in institutional-agents README
Step 5: Add acceptance-officer gate template and refusal eval
Step 6: Update all indexes (agents README, skills README, registry, inventory)
Step 7: Validate with agentic toolkit
Step 8: Commit and push
```

## Success Criteria

- [ ] git-session-branch-steward skill exists at `.claude/skills/git-session-branch-steward/SKILL.md`
- [ ] git-session-steward agent exists at `.claude/agents/git-session-steward.md`
- [ ] gcs-benchmark-steward skill exists at `.claude/skills/gcs-benchmark-steward/SKILL.md`
- [ ] Candidate role table cleaned (3 removed/merged)
- [ ] acceptance-officer has gate template and refusal eval at `docs/agentic/institutional-agents/005-acceptance-officer/`
- [ ] All indexes updated with new entries
- [ ] `python tools/agentic_design/agentic_toolkit.py validate-docs` passes
- [ ] `python tools/agentic_design/agentic_toolkit.py validate-skills` passes
- [ ] Changes committed and pushed to master
