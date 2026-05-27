# GCS Claude Code Skills Index

This directory contains Claude Code-compatible skill definitions converted
from the `.codex/skills/` directory. Each skill governs a specific module,
boundary, or process domain in the GCS project.

## Solver Core Skills

| Skill | Domain | Key trigger |
|-------|--------|-------------|
| [gcs-architecture-steward](gcs-architecture-steward/SKILL.md) | Cross-module architecture | Architecture doc changes, cross-module refactors, dependency direction |
| [gcs-kernel-contract-steward](gcs-kernel-contract-steward/SKILL.md) | Kernel contracts | Stable IDs, snapshots, state deltas, report codes |
| [gcs-constraint-semantics-steward](gcs-constraint-semantics-steward/SKILL.md) | Constraint catalog | Constraint definitions, evaluators, Jacobians, degeneracy |
| [gcs-incidence-structure-steward](gcs-incidence-structure-steward/SKILL.md) | Incidence graph | Hypergraphs, connectivity, structural projections |
| [gcs-decomposition-planning-steward](gcs-decomposition-planning-steward/SKILL.md) | Decomposition planner | Cover plans, boundary projections, solve DAGs |
| [gcs-numeric-engine-steward](gcs-numeric-engine-steward/SKILL.md) | Numeric engine | Local solves, residuals, Jacobians, numeric traces |
| [gcs-diagnostics-certification-steward](gcs-diagnostics-certification-steward/SKILL.md) | Diagnostics | DOF, rank, residual, gluing, obstruction evidence |
| [gcs-session-runtime-steward](gcs-session-runtime-steward/SKILL.md) | Session runtime | Commands, transactions, history, undo/redo |

## Boundary and Integration Skills

| Skill | Domain | Key trigger |
|-------|--------|-------------|
| [gcs-io-adapter-steward](gcs-io-adapter-steward/SKILL.md) | IO adapters | Scene schemas, serialization, migrations, round-trips |
| [gcs-viewer-bridge-steward](gcs-viewer-bridge-steward/SKILL.md) | Viewer bridge | Scene projection, diagnostic overlays, interaction commands |
| [gcs-scene-behavior-steward](gcs-scene-behavior-steward/SKILL.md) | Scene behavior | Scene formats, JSON behavior, history replay, IO compatibility |
| [gcs-cpp-solver-maintainer](gcs-cpp-solver-maintainer/SKILL.md) | C++ solver | src/gcs, CMake, CLI, C++23 module boundaries |
| [gcs-python-gui-builder](gcs-python-gui-builder/SKILL.md) | Python GUI | tkinter, matplotlib, viewer bridge, GUI behavior |
| [gcs-scene-generation-engineer](gcs-scene-generation-engineer/SKILL.md) | Scene generation | Synthetic graphs, validation, repair, fixture promotion |

## Quality and Governance Skills

| Skill | Domain | Key trigger |
|-------|--------|-------------|
| [gcs-quality-steward](gcs-quality-steward/SKILL.md) | Quality gates | Contract tests, CTest, negative fixtures, CI matrix |
| [gcs-contract-tools-steward](gcs-contract-tools-steward/SKILL.md) | Contract tools | Fixture builders, invariant checkers, golden reports |
| [gcs-third-party-governance-steward](gcs-third-party-governance-steward/SKILL.md) | Third-party governance | Dependencies, licensing, CMake adapters, SBOM |
| [gcs-ui-design-steward](gcs-ui-design-steward/SKILL.md) | UI design | Visual tokens, design-system conventions, visual QA |
| [gcs-scientific-figure-producer](gcs-scientific-figure-producer/SKILL.md) | Scientific figures | Figure specs, semantic composition, visual QA |

## Process Skills

| Skill | Domain | Key trigger |
|-------|--------|-------------|
| [task-scoped-session-closer](task-scoped-session-closer/SKILL.md) | Session closure | Task archives, evidence bundles, commit/push handoff |

## Institutional Agents

Agent role definitions live in `.claude/agents/`:

| Agent | Maturity | Purpose |
|-------|----------|---------|
| [bladesmith-quench-forge](../agents/bladesmith-quench-forge.md) | Practiced | Extract reusable operational lessons |
| [tailor-stitch-timeline](../agents/tailor-stitch-timeline.md) | Practiced | Maintain multi-session timelines |
| [atelier-steward-calibrate-review](../agents/atelier-steward-calibrate-review.md) | Seed | Review UI against design conventions |
| [art-director-frame-judge](../agents/art-director-frame-judge.md) | Seed | Independent visual judgment |
| [governance-sentinel](../agents/governance-sentinel.md) | Candidate | Permission and audit governance |
| [demo-producer](../agents/demo-producer.md) | Candidate | Product demo creation |
| [benchmark-scout](../agents/benchmark-scout.md) | Candidate | External solver comparison |
| [release-shepherd](../agents/release-shepherd.md) | Candidate | Release readiness |

## Conversion Notes

These skills are converted from `.codex/skills/` (Codex/OpenAI format). Key
changes from the originals:

1. **Removed `agents/openai.yaml`**: Codex-specific interface files replaced
   by Claude Code's native SKILL.md frontmatter
2. **Enhanced descriptions**: Frontmatter `description` fields are optimized
   for Claude Code's skill auto-invocation system
3. **Added "Claude Code Integration" sections**: Each skill now documents how
   to use Claude's specific tools (Read, Edit, Grep, Bash, Agent, MCP tools)
4. **Agent definitions centralized**: Institutional agents moved from
   `docs/agentic/institutional-agents/` to `.claude/agents/` with Claude Code
   frontmatter

The original `.codex/skills/` files remain intact as the authoritative source.
These `.claude/skills/` files are the operational Claude Code interface layer.
