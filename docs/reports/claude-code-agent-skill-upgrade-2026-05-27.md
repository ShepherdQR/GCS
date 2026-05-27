# Claude Code Agent & Skill Upgrade Report

**Date**: 2026-05-27
**Branch**: master
**Status**: Complete

## Executive Summary

This report documents the conversion of the GCS project's agent and skill
ecosystem from Codex/OpenAI format to Claude Code native format. The upgrade
creates 22 skills under `.claude/skills/`, 8 agent definitions under
`.claude/agents/`, a root `CLAUDE.md` entry point, and skills/agents index
files.

All original `.codex/skills/` files remain intact as the authoritative
source. The new `.claude/` files are the operational Claude Code interface.

---

## 1. Inventory Analysis

### 1.1 Source Material (Codex Format)

The project contained 22 skills under `.codex/skills/`, each structured as:

```
.codex/skills/<name>/
  SKILL.md           # YAML frontmatter (name, description) + skill content
  agents/openai.yaml  # Codex interface: display_name, short_description,
                      #   default_prompt, optional policy.allow_implicit_invocation
  references/         # Optional reference documents (present in 5 skills)
```

The skills cover three layers:

**Solver Core (8 skills)**:
- `gcs-architecture-steward` — Cross-module architecture decisions
- `gcs-kernel-contract-steward` — Stable IDs, snapshots, state deltas
- `gcs-constraint-semantics-steward` — Constraint definitions, evaluators, Jacobians
- `gcs-incidence-structure-steward` — Incidence hypergraphs, connectivity
- `gcs-decomposition-planning-steward` — Cover plans, solve DAGs
- `gcs-numeric-engine-steward` — Local solves, residuals, numeric traces
- `gcs-diagnostics-certification-steward` — DOF, rank, gluing, obstruction
- `gcs-session-runtime-steward` — Commands, transactions, history, undo/redo

**Boundary/Integration (6 skills)**:
- `gcs-io-adapter-steward` — Scene schemas, serialization, migrations
- `gcs-viewer-bridge-steward` — Scene projection, overlays, commands
- `gcs-scene-behavior-steward` — Scene formats, JSON, history replay
- `gcs-cpp-solver-maintainer` — C++ modules, CMake, CLI
- `gcs-python-gui-builder` — tkinter, matplotlib, viewer bridge
- `gcs-scene-generation-engineer` — Synthetic graph generation, validation

**Quality/Governance/Process (7 skills)**:
- `gcs-quality-steward` — Contract tests, CTest, negative fixtures
- `gcs-contract-tools-steward` — Fixture builders, invariant checkers
- `gcs-third-party-governance-steward` — Dependencies, licensing
- `gcs-ui-design-steward` — Visual tokens, design-system conventions
- `gcs-scientific-figure-producer` — Figure specs, semantic composition
- `task-scoped-session-closer` — Task archives, evidence bundles

Plus 4 institutional agents tracked in
`docs/agentic/institutional-agent-registry-and-scorecard.md`:

| ID | Agent | Maturity | Score |
|----|-------|----------|-------|
| I001 | Bladesmith: Quench-Forge | Practiced | 9/10 |
| I002 | Tailor: Stitch-Timeline | Practiced | 8/10 |
| I003 | Atelier Steward: Calibrate-Review | Seed | 6/10 |
| I004 | Art Director: Frame-Judge | Seed | 6/10 |

And 4 candidate agents in the backlog: Governance Sentinel, Demo Producer,
Benchmark Scout, Release Shepherd.

### 1.2 Format Comparison

| Aspect | Codex (.codex/skills/) | Claude Code (.claude/skills/) |
|--------|------------------------|-------------------------------|
| Skill definition | SKILL.md with YAML frontmatter | SKILL.md with YAML frontmatter |
| Interface config | agents/openai.yaml | Embedded in SKILL.md frontmatter |
| Invocation | `$skill-name` syntax in prompt | Skill tool with name matching |
| Auto-invoke | `allow_implicit_invocation` policy | Description-based pattern matching |
| Agent roles | Separate agent yaml files | `.claude/agents/*.md` files |
| Tool mapping | Implicit (model-dependent) | Explicit in "Claude Code Integration" section |

---

## 2. Upgrade Design

### 2.1 Key Changes

1. **Removed `agents/openai.yaml`**: The Codex-specific interface layer is
   replaced by Claude Code's native SKILL.md frontmatter. The `display_name`,
   `short_description`, and `default_prompt` fields from openai.yaml are
   absorbed into enhanced frontmatter descriptions.

2. **Enhanced descriptions**: Frontmatter `description` fields are optimized
   for Claude Code's auto-invocation pattern matching. Descriptions now include
   more trigger keywords and context clues.

3. **Added "Claude Code Integration" sections**: Every skill now documents how
   to use Claude's specific tools:
   - `Read` — for reading architecture docs and reference files
   - `Edit` — for surgical code changes
   - `Write` — for creating new artifacts
   - `Grep` — for finding callers, consumers, and patterns
   - `Glob` — for file pattern matching
   - `Bash` — for build, test, and validation commands
   - `Agent` — for spawnable exploration tasks
   - `TaskCreate` / `TaskUpdate` — for work tracking
   - MCP tools — `mcp__Claude_Preview__*`, `mcp__Claude_in_Chrome__*` for
     visual review and figure production

4. **Agent definitions centralized**: Institutional agents moved from
   `docs/agentic/institutional-agents/<id>/README.md` to `.claude/agents/<name>.md`
   with Claude Code frontmatter and integration notes. Candidate backlog agents
   are also defined.

5. **Root CLAUDE.md**: New project entry point documenting skill/agent
   organization, key architecture docs, build commands, and workspace
   conventions.

### 2.2 File Inventory (Created)

```
.claude/
  skills/
    README.md                                    # Skills index
    gcs-architecture-steward/SKILL.md
    gcs-constraint-semantics-steward/SKILL.md
    gcs-contract-tools-steward/SKILL.md
    gcs-cpp-solver-maintainer/SKILL.md
    gcs-decomposition-planning-steward/SKILL.md
    gcs-diagnostics-certification-steward/SKILL.md
    gcs-incidence-structure-steward/SKILL.md
    gcs-io-adapter-steward/SKILL.md
    gcs-kernel-contract-steward/SKILL.md
    gcs-numeric-engine-steward/SKILL.md
    gcs-python-gui-builder/SKILL.md
    gcs-quality-steward/SKILL.md
    gcs-scene-behavior-steward/SKILL.md
    gcs-scene-generation-engineer/SKILL.md
    gcs-scientific-figure-producer/SKILL.md
    gcs-session-runtime-steward/SKILL.md
    gcs-third-party-governance-steward/SKILL.md
    gcs-ui-design-steward/SKILL.md
    gcs-viewer-bridge-steward/SKILL.md
    task-scoped-session-closer/SKILL.md
  agents/
    README.md                                    # Agents index
    bladesmith-quench-forge.md                   # I001 — Practiced
    tailor-stitch-timeline.md                    # I002 — Practiced
    atelier-steward-calibrate-review.md          # I003 — Seed
    art-director-frame-judge.md                  # I004 — Seed
    governance-sentinel.md                       # Candidate
    demo-producer.md                             # Candidate
    benchmark-scout.md                           # Candidate
    release-shepherd.md                          # Candidate
CLAUDE.md                                        # Root project entry point
```

---

## 3. Integration Notes

### 3.1 Skill Auto-Invocation

Claude Code matches skills to user requests via the `description` frontmatter
field. The upgraded descriptions are designed for high-precision matching:

- **Domain keywords**: Each description lists specific technical terms
  (`NumericTask`, `ModelSnapshot`, `IncidenceHypergraph`, etc.) that trigger
  the correct skill when those concepts appear in a user request.
- **Action keywords**: Descriptions include action verbs (`designing`,
  `reviewing`, `editing`, `generating`) to match intent.
- **Path keywords**: File paths (`src/gcs`, `python/gcs_viz`,
  `fixtures/scene`, `CMakeLists.txt`) trigger the appropriate skill.

### 3.2 Coordination Between Skills

Many skills reference peers for cross-domain work. For example,
`gcs-scene-behavior-steward` directs users to also invoke
`gcs-cpp-solver-maintainer` for C++ changes and `gcs-python-gui-builder` for
GUI replay changes. Claude Code handles this through its Skill tool, which can
chain multiple skill invocations.

### 3.3 Institutional Agent Invocation

Institutional agents are invoked via the Agent tool with the agent's name.
Unlike module stewards, institutional agents operate on project memory and
process rather than code.

### 3.4 MCP Tool Integration

Several skills integrate with Claude Code's MCP tools:

- **Claude Preview** (`mcp__Claude_Preview__*`): Used by `gcs-ui-design-steward`,
  `gcs-scientific-figure-producer`, `atelier-steward-calibrate-review`, and
  `art-director-frame-judge` for visual inspection of rendered UI and figures.
- **Claude in Chrome** (`mcp__Claude_in_Chrome__*`): Used by
  `gcs-scientific-figure-producer` for browser-based figure composition and
  `demo-producer` for recording demos.
- **CCD Session** (`mcp__ccd_session__*`): Used by `task-scoped-session-closer`
  for session chapter marking.

---

## 4. Next Steps

### 4.1 Immediate

- [x] All 22 skills converted to `.claude/skills/`
- [x] All 8 agent definitions created in `.claude/agents/`
- [x] Root `CLAUDE.md` entry point created
- [x] This report documented and archived
- [ ] Commit and push to remote

### 4.2 Short-Term

- **Skill calibration**: Test auto-invocation accuracy by running representative
  tasks in each domain and verifying the correct skill is matched.
- **Agent evidence gathering**: Collect additional examples for seed-level
  agents (Atelier Steward, Art Director) to enable promotion to practiced.
- **Candidate agent development**: Create prompts, templates, and refusal evals
  for Governance Sentinel as the highest-priority candidate.

### 4.3 Medium-Term

- **Skill iteration**: Refine descriptions based on invocation accuracy data.
  If a skill is not auto-invoked when it should be, add trigger keywords.
- **Agent promotion**: Review the agent registry scorecard when institutional
  agents gain additional examples. Follow the promotion rule: promote only with
  evidence, not because the name is appealing.
- **Tool integration expansion**: As new MCP tools become available, update the
  "Claude Code Integration" sections of affected skills.

### 4.4 Maintenance Policy

- **Source of truth**: `docs/architecture/` remains authoritative for solver
  contracts. `.codex/skills/` remains the bridge between architecture and
  implementation. `.claude/skills/` is the operational interface layer.
- **Sync rule**: When a `.codex/skills/<name>/SKILL.md` is substantively
  changed, the corresponding `.claude/skills/<name>/SKILL.md` should be updated
  within the same change.
- **Drift detection**: Run `diff -r .codex/skills/ .claude/skills/` (excluding
  `agents/` subdirectories and "Claude Code Integration" sections) during
  periodic repository health checks.

---

## Appendix A: Conversion Mapping

| Codex Skill | Claude Code Skill | Reference files preserved |
|-------------|-------------------|--------------------------|
| `.codex/skills/gcs-architecture-steward/` | `.claude/skills/gcs-architecture-steward/` | `references/architecture-map.md` |
| `.codex/skills/gcs-constraint-semantics-steward/` | `.claude/skills/gcs-constraint-semantics-steward/` | — |
| `.codex/skills/gcs-contract-tools-steward/` | `.claude/skills/gcs-contract-tools-steward/` | — |
| `.codex/skills/gcs-cpp-solver-maintainer/` | `.claude/skills/gcs-cpp-solver-maintainer/` | `references/cpp-solver-map.md` |
| `.codex/skills/gcs-decomposition-planning-steward/` | `.claude/skills/gcs-decomposition-planning-steward/` | — |
| `.codex/skills/gcs-diagnostics-certification-steward/` | `.claude/skills/gcs-diagnostics-certification-steward/` | — |
| `.codex/skills/gcs-incidence-structure-steward/` | `.claude/skills/gcs-incidence-structure-steward/` | — |
| `.codex/skills/gcs-io-adapter-steward/` | `.claude/skills/gcs-io-adapter-steward/` | — |
| `.codex/skills/gcs-kernel-contract-steward/` | `.claude/skills/gcs-kernel-contract-steward/` | — |
| `.codex/skills/gcs-numeric-engine-steward/` | `.claude/skills/gcs-numeric-engine-steward/` | — |
| `.codex/skills/gcs-python-gui-builder/` | `.claude/skills/gcs-python-gui-builder/` | `references/python-gui-map.md` |
| `.codex/skills/gcs-quality-steward/` | `.claude/skills/gcs-quality-steward/` | — |
| `.codex/skills/gcs-scene-behavior-steward/` | `.claude/skills/gcs-scene-behavior-steward/` | `references/scene-behavior-contract.md` |
| `.codex/skills/gcs-scene-generation-engineer/` | `.claude/skills/gcs-scene-generation-engineer/` | `references/scene-generation-map.md` |
| `.codex/skills/gcs-scientific-figure-producer/` | `.claude/skills/gcs-scientific-figure-producer/` | — |
| `.codex/skills/gcs-session-runtime-steward/` | `.claude/skills/gcs-session-runtime-steward/` | — |
| `.codex/skills/gcs-third-party-governance-steward/` | `.claude/skills/gcs-third-party-governance-steward/` | — |
| `.codex/skills/gcs-ui-design-steward/` | `.claude/skills/gcs-ui-design-steward/` | — |
| `.codex/skills/gcs-viewer-bridge-steward/` | `.claude/skills/gcs-viewer-bridge-steward/` | — |
| `.codex/skills/task-scoped-session-closer/` | `.claude/skills/task-scoped-session-closer/` | — |

## Appendix B: Agent Maturity Progression

```
Candidate → Seed → Practiced → Promoted → Institutional
```

Current state:
- **Institutional**: None yet
- **Practiced**: Bladesmith (I001), Tailor (I002)
- **Seed**: Atelier Steward (I003), Art Director (I004)
- **Candidate**: Governance Sentinel, Demo Producer, Benchmark Scout,
  Release Shepherd

---

*Report generated by Claude Code agent/skill upgrade workflow, 2026-05-27.*
