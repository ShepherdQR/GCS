# Gardener Maintenance Record: 001 -- Post-Orchestration Garden Scan

**Date**: 2026-05-30
**Scope**: Post multi-agent orchestration implementation cleanup
**Agent**: Gardener: Prune-Nourish (I008), seed

## Survey Results

The following issues were discovered during a scan of `.claude/skills/`, `docs/agentic/`, and agent definition files:

### 1. Stale absolute paths (1 file affected)

**File**: `docs/agentic/nightly-runs/2026-05-27/README.md` line 42
**Issue**: Three markdown links used absolute Windows paths from a stale worktree:
- `/C:/Users/QR/.codex/worktrees/216a/GCS/docs/agentic/nightly-runs/2026-05-27/commands.md`
- `/C:/Users/QR/.codex/worktrees/216a/GCS/docs/agentic/nightly-runs/2026-05-27/findings.json`
- `/C:/Users/QR/.codex/worktrees/216a/GCS/docs/agentic/nightly-runs/2026-05-27/repair-plan.md`
**Status**: FIXED -- replaced with relative paths (`commands.md`, `findings.json`, `repair-plan.md`)
**Verification**: Files confirmed to exist in same directory.

### 2. Broken relative links (1 file, 26 occurrences)

**File**: `docs/agentic/agent-skill-asset-inventory.md`
**Issue**: Links to skill files used `.claude/skills/...` without the parent directory prefix. From `docs/agentic/`, `.claude/` does not resolve (it would look for `docs/agentic/.claude/`).
**Status**: FIXED -- all 26 occurrences changed from `(.claude/skills/` to `(../../.claude/skills/` using `replace_all`.
**Verification**: Path from `docs/agentic/` → `../../` → repo root → `.claude/skills/` resolves correctly.

### 3. Skills missing `model` frontmatter field (3 files)

**Issue**: The new convention (established during orchestration work) requires all skills to have `model` and `priority` fields. Three skills had `priority` but were missing `model`:

| Skill | Had priority? | Had model? |
|-------|:---:|:---:|
| `gcs-architecture-steward` | yes (85) | no |
| `gcs-cpp-solver-maintainer` | yes (70) | no |
| `gcs-ui-qa-steward` | yes (65) | no |

**Status**: FIXED -- all three received `model: sonnet`
**Rationale**: `sonnet` is the appropriate default for steward/analyst skills. `opus` is reserved for multi-agent orchestration roles (orchestrator, session-close-orchestrator).
**Verification**: Frontmatter re-read; model field confirmed present.

### 4. Skills missing BOTH `model` and `priority` (22 files)

**Issue**: 22 additional skills have neither `model` nor `priority` in their frontmatter:

| Category | Skills |
|----------|--------|
| Solver core (8) | kernel-contract, constraint-semantics, incidence-structure, decomposition-planning, numeric-engine, diagnostics-certification, session-runtime, quality |
| Boundary/integration (4) | io-adapter, viewer-bridge, scene-behavior, python-gui-builder, scene-generation-engineer, contract-tools |
| Governance (2) | third-party-governance, ui-design, scientific-figure-producer |
| Audit/demo (4) | repository-audit, token-audit, product-demo, benchmark |
| Process (2) | task-scoped-session-closer, git-session-branch |

**Status**: NOT FIXED (escalated)
**Escalation rationale**: Adding both `model` and `priority` to 22 skills requires deciding per-skill priority ordering and model assignment. This crosses from maintenance into design -- priority values encode workflow precedence, and model assignments should be based on task complexity analysis per skill. This should be handled as a dedicated task card, not a gardener batch.

### 5. TODO/FIXME scan

**Scope**: `.claude/skills/` and `docs/agentic/`
**Finding**: No TODO or FIXME comments found. Clean state.

### 6. Broken internal .md links

**Scope**: `docs/agentic/` (all .md files)
**Finding**: Beyond issue #2 (already fixed), no other broken internal links detected. Cross-references in `critical-issues-registry.md` to `docs/research/token-economics-*.md` files were verified to resolve correctly.

## Items Fixed (5)

| # | File | Change | Type |
|---|------|--------|------|
| 1 | `docs/agentic/nightly-runs/2026-05-27/README.md` | Absolute → relative paths (3 links) | Stale path |
| 2 | `docs/agentic/agent-skill-asset-inventory.md` | `.claude/skills/` → `../../.claude/skills/` (26 occurrences) | Broken link |
| 3 | `.claude/skills/gcs-architecture-steward/SKILL.md` | Added `model: sonnet` | Missing frontmatter |
| 4 | `.claude/skills/gcs-cpp-solver-maintainer/SKILL.md` | Added `model: sonnet` | Missing frontmatter |
| 5 | `.claude/skills/gcs-ui-qa-steward/SKILL.md` | Added `model: sonnet` | Missing frontmatter |

## Items Escalated (1)

| # | Issue | Rationale | Recommended path |
|---|-------|-----------|-----------------|
| 1 | 22 skills missing both `model` and `priority` | Requires design decisions (priority ordering, model selection per skill complexity) plus priority values must not conflict with orchestrator (100), task-intake (95), session-close (90), architecture (85), solver (70), ui-qa (65). This is architecture-level convention work. | Task card: "Standardize skill frontmatter with model and priority fields" -- assign to `gcs-architecture-steward` or bladesmith (I001) for convention standardization |

## Affected Files Summary

```
docs/agentic/nightly-runs/2026-05-27/README.md        (1 edit: stale paths)
docs/agentic/agent-skill-asset-inventory.md            (1 edit: 26 link fixes)
.claude/skills/gcs-architecture-steward/SKILL.md       (1 edit: +model field)
.claude/skills/gcs-cpp-solver-maintainer/SKILL.md      (1 edit: +model field)
.claude/skills/gcs-ui-qa-steward/SKILL.md              (1 edit: +model field)
```

## Verification

- **No behavior change**: All fixes are path corrections or frontmatter additions. No solver semantics, module contracts, public APIs, fixture behavior, stable IDs, quality gates, or test assertions were touched.
- **Scope confirmed**: 5 files, 5 logical changes, all within documentation and skill metadata.
- **Build check**: Not applicable (no C++/Python source changes).
- **Escalation criteria applied**: The 22-skill frontmatter gap exceeds gardener scope because assigning priorities and models requires domain judgment about skill ordering and complexity. This is correctly escalated to a task card.

## Gardener Growth Notes

- This was the gardener's first real maintenance cycle (I008, seed maturity).
- The survey found 6 distinct issue categories but only 3 were gardener-scope.
- The escalation boundary held correctly: path/formatting fixes are safe; priority/value decisions are not.
- Future cycles should check for `.codex` reference staleness as skills evolve in both directories.
