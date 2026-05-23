# Physical Agent Skill Catalog

## Purpose

This catalog records the physical Codex skills generated from
`62-module-agents.md`. These skills live under `.codex/skills/` and turn the
module-agent design into reusable project-local operating procedures.

The skills are architecture and maintenance overlays. They do not become C++23
solver runtime dependencies.

## Skill Map

| Module / concern | Physical skill | Primary design source |
| --- | --- | --- |
| Kernel contracts | `.codex/skills/gcs-kernel-contract-steward` | `62-module-agents.md`, `63-target-contract-interface-implementation-test-design.md` |
| Constraint semantics | `.codex/skills/gcs-constraint-semantics-steward` | `62-module-agents.md`, `63-target-contract-interface-implementation-test-design.md` |
| Incidence structure | `.codex/skills/gcs-incidence-structure-steward` | `62-module-agents.md`, `63-target-contract-interface-implementation-test-design.md` |
| Decomposition planning | `.codex/skills/gcs-decomposition-planning-steward` | `62-module-agents.md`, `63-target-contract-interface-implementation-test-design.md` |
| Numeric engine | `.codex/skills/gcs-numeric-engine-steward` | `62-module-agents.md`, `63-target-contract-interface-implementation-test-design.md` |
| Diagnostics certification | `.codex/skills/gcs-diagnostics-certification-steward` | `62-module-agents.md`, `63-target-contract-interface-implementation-test-design.md` |
| Session runtime | `.codex/skills/gcs-session-runtime-steward` | `62-module-agents.md`, `63-target-contract-interface-implementation-test-design.md` |
| IO adapters | `.codex/skills/gcs-io-adapter-steward` | `62-module-agents.md`, `63-target-contract-interface-implementation-test-design.md` |
| Viewer bridge | `.codex/skills/gcs-viewer-bridge-steward` | `62-module-agents.md`, `63-target-contract-interface-implementation-test-design.md` |
| Contract tools | `.codex/skills/gcs-contract-tools-steward` | `62-module-agents.md`, `63-target-contract-interface-implementation-test-design.md` |
| Quality gates | `.codex/skills/gcs-quality-steward` | `62-module-agents.md`, `63-target-contract-interface-implementation-test-design.md` |
| Third-party governance | `.codex/skills/gcs-third-party-governance-steward` | `62-module-agents.md`, `third-party-policy.md` |

## Skill Contract

Each physical skill must provide:

- `SKILL.md` with frontmatter `name` and `description`;
- `agents/openai.yaml` with display metadata and default prompt;
- a module-specific workflow;
- ownership boundaries;
- refused decisions;
- required structured design output;
- references back to the architecture source of truth.

## Operating Rule

When a future task touches one module deeply, use that module's physical skill
after the broad `gcs-architecture-steward` boundary check. When a task spans
implementation or tests, pair the module skill with `gcs-cpp-solver-maintainer`
or `gcs-quality-steward` as appropriate.
