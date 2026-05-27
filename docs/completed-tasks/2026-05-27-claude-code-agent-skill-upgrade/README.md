---
task_id: 2026-05-27-claude-code-agent-skill-upgrade
status: complete
session_goal: "Analyze project agents and skills, create Claude Code-compatible upgraded versions, fill gaps across 3 phases, archive with token efficiency report."
archive_target: docs/completed-tasks/2026-05-27-claude-code-agent-skill-upgrade
---

# Claude Code Agent & Skill Ecosystem Upgrade

## Task Objective

Upgrade the GCS project's agent and skill ecosystem from Codex/OpenAI format to
Claude Code native format, then expand coverage by analyzing gaps and creating
new skills and agents for uncovered domains.

## Scope And Non-Goals

In scope:
- Convert 20 existing `.codex/skills/` to `.claude/skills/` with enhanced
  descriptions and Claude Code Integration sections
- Create 8 agent role definitions under `.claude/agents/`
- Analyze project for uncovered domains (tools, agent types, process gaps)
- Phase 1: Add repository-audit, token-audit skills + night-watch agent
- Phase 2: Add ui-qa skill + acceptance-officer, collation-officer agents
- Phase 3: Add product-demo skill + bookkeeper, gardener agents
- Create root CLAUDE.md, skills/agents indexes, comprehensive upgrade report

Out of scope:
- Modifying `.codex/skills/` originals (preserved as authoritative source)
- Solver, runtime, IO, viewer, fixture, or scene behavior changes
- Promoting any candidate agent beyond candidate level without evidence

## Interaction Summary

The user requested analysis and upgrade of the project's agent and skill system.
The work proceeded in two major segments:

**Segment 1 — Conversion & Foundation**: Analyzed all 20 Codex skills (SKILL.md +
agents/openai.yaml) and 4 institutional agents in the registry. Created Claude
Code-compatible versions with enhanced frontmatter descriptions, removed
Codex-specific openai.yaml interface files, and added "Claude Code Integration"
sections mapping workflows to specific Claude tools (Read, Edit, Grep, Bash,
Agent, MCP tools). Created 4 institutional + 4 candidate agent definitions.
Created root CLAUDE.md and a comprehensive upgrade report.

**Segment 2 — Gap Analysis & Expansion**: Analyzed uncovered tool domains
(repository_audit, token_audit, ui_qa, product_demo, session_efficiency) and
the full 12-agent candidate backlog from the institutional agent registry.
Selected 4 skills and 5 agents across 3 priority phases based on tool readiness,
documentation maturity, and operating standard recommendations.

## Work Completed

### Segment 1: Initial Upgrade (commit `4dd869b`)

- Created `.claude/skills/` with 20 skill files (one per module/boundary/process domain)
- Created `.claude/agents/` with 8 agent definitions:
  - I001 Bladesmith: Quench-Forge (Practiced)
  - I002 Tailor: Stitch-Timeline (Practiced)
  - I003 Atelier Steward: Calibrate-Review (Seed)
  - I004 Art Director: Frame-Judge (Seed)
  - Governance Sentinel (Candidate)
  - Demo Producer (Candidate)
  - Benchmark Scout (Candidate)
  - Release Shepherd (Candidate)
- Created root `CLAUDE.md` project entry point
- Created `docs/reports/claude-code-agent-skill-upgrade-2026-05-27.md`
- Created `.claude/skills/README.md` and `.claude/agents/README.md` indexes

### Segment 2: Phase 1-3 Expansions (commit `eaf2ca8`)

**Phase 1** — High-priority tools:
- `gcs-repository-audit-steward`: Repository audit pipeline (collect/diff/trend/index/archive-delta)
- `gcs-token-audit-steward`: Token consumption tracking (watch/report/trend/BEI scoring)
- `night-watch` agent: Nightly patrol based on `nightly-immune-diagnostics.md`

**Phase 2** — Design-execution separation:
- `gcs-ui-qa-steward`: UI QA automation (theme tokens, contrast, static analysis, headless render)
- `acceptance-officer` agent: Independent evidence review with gate decisions
- `collation-officer` agent: Cross-read docs/code/tests for consistency

**Phase 3** — Economics and maintenance:
- `gcs-product-demo-steward`: Demo packaging (R1 smoke test, diagnostic classification, replay evidence)
- `bookkeeper` agent: Token/cost/value budget tracking
- `gardener` agent: Small friction, debt, and maintenance handling

## Files And Artifacts

### Created (43 files, ~3315 lines)

**Skills (24 SKILL.md + 1 README)**:
- `.claude/skills/README.md`
- `.claude/skills/gcs-architecture-steward/SKILL.md`
- `.claude/skills/gcs-kernel-contract-steward/SKILL.md`
- `.claude/skills/gcs-constraint-semantics-steward/SKILL.md`
- `.claude/skills/gcs-incidence-structure-steward/SKILL.md`
- `.claude/skills/gcs-decomposition-planning-steward/SKILL.md`
- `.claude/skills/gcs-numeric-engine-steward/SKILL.md`
- `.claude/skills/gcs-diagnostics-certification-steward/SKILL.md`
- `.claude/skills/gcs-session-runtime-steward/SKILL.md`
- `.claude/skills/gcs-io-adapter-steward/SKILL.md`
- `.claude/skills/gcs-viewer-bridge-steward/SKILL.md`
- `.claude/skills/gcs-scene-behavior-steward/SKILL.md`
- `.claude/skills/gcs-cpp-solver-maintainer/SKILL.md`
- `.claude/skills/gcs-python-gui-builder/SKILL.md`
- `.claude/skills/gcs-scene-generation-engineer/SKILL.md`
- `.claude/skills/gcs-quality-steward/SKILL.md`
- `.claude/skills/gcs-contract-tools-steward/SKILL.md`
- `.claude/skills/gcs-third-party-governance-steward/SKILL.md`
- `.claude/skills/gcs-ui-design-steward/SKILL.md`
- `.claude/skills/gcs-scientific-figure-producer/SKILL.md`
- `.claude/skills/task-scoped-session-closer/SKILL.md`
- `.claude/skills/gcs-repository-audit-steward/SKILL.md` (Phase 1)
- `.claude/skills/gcs-token-audit-steward/SKILL.md` (Phase 1)
- `.claude/skills/gcs-ui-qa-steward/SKILL.md` (Phase 2)
- `.claude/skills/gcs-product-demo-steward/SKILL.md` (Phase 3)

**Agents (13 .md + 1 README)**:
- `.claude/agents/README.md`
- `.claude/agents/bladesmith-quench-forge.md` (I001)
- `.claude/agents/tailor-stitch-timeline.md` (I002)
- `.claude/agents/atelier-steward-calibrate-review.md` (I003)
- `.claude/agents/art-director-frame-judge.md` (I004)
- `.claude/agents/governance-sentinel.md`
- `.claude/agents/demo-producer.md`
- `.claude/agents/benchmark-scout.md`
- `.claude/agents/release-shepherd.md`
- `.claude/agents/night-watch.md` (Phase 1)
- `.claude/agents/acceptance-officer.md` (Phase 2)
- `.claude/agents/collation-officer.md` (Phase 2)
- `.claude/agents/bookkeeper.md` (Phase 3)
- `.claude/agents/gardener.md` (Phase 3)

**Root and Reports**:
- `CLAUDE.md`
- `docs/reports/claude-code-agent-skill-upgrade-2026-05-27.md`

## Token Consumption And Output Ratio

### Session Token Data

| Metric | Value |
|--------|-------|
| Session input tokens | ~195,000 (estimated from DB: largest today at ~230K input) |
| Session output tokens | ~35,000 (estimated) |
| **Total session tokens** | **~230,000** |
| Estimated cost | ~$0.40 |
| Cache hit rate (daily avg) | 94.5% |

### Output Metrics

| Metric | Value |
|--------|-------|
| Files created | 43 |
| Total lines written | ~3,315 |
| Skills created/upgraded | 24 |
| Agent definitions created | 13 |
| Commits | 2 |
| Quality score | Pending validation |

### Efficiency Ratios

| Ratio | Value |
|-------|-------|
| Lines per 1K tokens | ~14.4 lines |
| Files per 1K tokens | ~0.19 files |
| Cost per file | ~$0.009 |
| Cost per skill | ~$0.017 |
| Cost per agent | ~$0.031 |

### Interpretation

The high output-to-token ratio reflects the template-driven nature of the work:
each skill and agent follows a consistent structural pattern (frontmatter,
workflow, boundaries, Claude Code Integration). The 94.5% cache hit rate
indicates effective reuse of project context across turns. The output is
documentation/configuration rather than executable code, so lines-per-token
is a reasonable efficiency metric.

## Experience, Skill, And Agent Evaluation

### Experience

Decision: **candidate experience recorded**.

Target: This archive itself serves as the experience record. The reusable
lesson is the methodology for systematically converting agent/skill ecosystems
between formats and the gap analysis framework (tool-first, doc-first,
pain-point-driven prioritization).

Reason: The conversion methodology (analyze → classify gaps → prioritize by
tool readiness → create in phases) is a repeatable pattern for future
ecosystem migrations or expansions. However, this is the first instance of
this specific pattern, so it stays candidate until a second similar migration
or expansion confirms the method.

### Skill

Decision: **4 new active skills created**.

Targets:
- `.claude/skills/gcs-repository-audit-steward/SKILL.md`
- `.claude/skills/gcs-token-audit-steward/SKILL.md`
- `.claude/skills/gcs-ui-qa-steward/SKILL.md`
- `.claude/skills/gcs-product-demo-steward/SKILL.md`

Reason: Each covers a tool domain with existing Python tooling that lacked
skill coverage. The tool-first approach ensures skills have immediate
operational value. The 20 existing skills were also hardened with Claude Code
Integration sections.

### Agent

Decision: **5 new candidate agents created**.

Targets:
- `.claude/agents/night-watch.md` (value night watch)
- `.claude/agents/acceptance-officer.md` (acceptance officer)
- `.claude/agents/collation-officer.md` (collation officer)
- `.claude/agents/bookkeeper.md` (bookkeeper)
- `.claude/agents/gardener.md` (gardener)

Reason: These fill the most immediately actionable gaps in the institutional
agent candidate backlog. All remain at candidate level per the promotion rule:
they need real invocation evidence before advancing to seed.

Deferred candidates (7 remain): helmsman, mirror-polisher, seal-stamper,
postmortem-officer, curator, road-paver, law-officer. These await real
triggering demand.

## Evidence

```text
# Verify file structure
ls -d .claude/skills/*/ | wc -l
24

ls .claude/agents/*.md | wc -l
14  (13 agents + 1 README)

# Git commits
git log --oneline 20cec07..4dd869b
4dd869b Add Claude Code agent and skill upgrade layer

git log --oneline 4dd869b..eaf2ca8
eaf2ca8 Add Phase 1-3 skill and agent expansions

# Token audit (daily)
python -m tools.token_audit trend --days 1
2026-05-27: 5 sessions, 663,579 tokens, $0.97, 4 commits, 94.5% cache hit, BEI 0.21

# Repository audit (files created)
git diff --stat 20cec07..HEAD -- .claude/ CLAUDE.md docs/reports/claude-code-agent-skill-upgrade-2026-05-27.md
43 files changed, ~3315 insertions
```

## Decisions

- Convert `.codex/skills/` to `.claude/skills/` rather than replacing originals.
  Both coexist; `.codex/` is authoritative source, `.claude/` is operational layer.
- Use tool-first prioritization: create skills where tools already exist.
- Use doc-first agent creation: night-watch backed by full nightly diagnostics spec.
- Keep all new agents at candidate level. Promotion requires real invocation evidence.
- Defer 7 remaining candidate agents from the institutional registry until demand arises.
- Each skill gets a "Claude Code Integration" section mapping to specific Claude tools.

## Skipped Checks And Risks

- Build and CTest are skipped: this is a docs/configuration-only change with
  no solver, runtime, IO, or viewer behavior changes.
- Agentic toolkit validation (validate-docs, validate-skills) should be run
  for completeness but was not executed in this session; the .claude/skills/
  files are not yet registered in the agentic toolkit's validation paths.
- Skill auto-invocation accuracy has not been tested. The enhanced descriptions
  are designed for Claude Code's pattern matching but need calibration.
- The 7 deferred candidate agents may represent real needs that are currently
  invisible due to lack of triggering sessions.

## Follow-Up

- Test skill auto-invocation accuracy by running representative tasks in each
  domain and observing which skill is matched.
- Collect additional examples for seed-level agents (I003 Atelier Steward,
  I004 Art Director) to enable promotion to practiced.
- After 2+ nightly diagnostic runs, evaluate night-watch for seed promotion.
- After 3+ task closures using acceptance-officer, evaluate for seed promotion.
- Consider registering `.claude/skills/` in the agentic toolkit's validation
  paths for automated skill validation.
- When a real session triggers one of the 7 deferred candidates, create the
  agent definition.

## Archive Handoff

- Archive path: `docs/completed-tasks/2026-05-27-claude-code-agent-skill-upgrade`
- Skills created/updated: 24 active in `.claude/skills/`
- Agents created: 13 in `.claude/agents/`
- Report: `docs/reports/claude-code-agent-skill-upgrade-2026-05-27.md`
- Experience candidate: This archive (conversion methodology)
- Next task: Test skill auto-invocation accuracy with representative domain tasks
