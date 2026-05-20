# Topos Semantic Model

## Purpose

Topos theory is useful for GCS as an architectural discipline, not as an
implementation requirement. The solver should not expose abstract category
theory where domain terms are clearer. The value is the local-to-global view:

```text
local geometric contexts produce local state sections
compatible local sections glue into a global proposed state
failed gluing produces an explicit diagnostic obstruction
```

This keeps decomposition, numeric solving, diagnostics, and runtime commits
under one semantics without forcing every module to know advanced mathematics.

## Finite Site

GCS works over a finite computational site built from one immutable model
snapshot:

- the whole model context;
- connected-component contexts;
- rigid-set and body-level contexts;
- decomposition subproblem contexts;
- overlap or boundary contexts shared by subproblems;
- gauge or anchor contexts used to choose representatives.

The planner chooses covers of the whole model by smaller contexts. A cover is
valid only when every active entity, constraint, boundary variable, and gauge
choice is accounted for by an explicit contract.

## Correspondence

| Topos term | GCS architecture term | Engineering meaning |
| --- | --- | --- |
| Site object | `ContextSnapshot` | A typed local view of the model. |
| Cover | `CoverPlan` | Subcontexts selected for decomposition. |
| Presheaf | State/report projection family | How model state and reports restrict to contexts. |
| Section | Local solve proposal | Coordinates and report over one context. |
| Restriction | Boundary projection | The local data visible on a smaller overlap. |
| Gluing | Assembly verification | Compatibility check and global proposal construction. |
| Obstruction | Diagnostic failure certificate | Why local proposals cannot become a global state. |
| Quotient/groupoid | `GaugePolicy` | Equivalent states under rigid motion or anchors. |

These names are architectural contracts. Source code can use domain vocabulary
when it is clearer, but it should preserve the same information.

## Required Contracts

Every decomposition-aware solve must be able to name:

- the context it is solving;
- the variables and constraints active in that context;
- the boundary variables exposed to other contexts;
- the restriction/projection used on overlaps;
- the gauge policy used to select a representative state;
- the compatibility metric used during gluing;
- the obstruction report produced when compatibility fails.

The numeric engine returns local sections and numeric evidence. It does not
decide whether a family of local sections is globally meaningful. Diagnostics
and the runtime own that decision through gluing and verification reports.

## Diagnostic Interpretation

The same status vocabulary becomes sharper under this model:

- `under_constrained`: more than one compatible global section exists modulo
  the declared gauge policy.
- `over_constrained`: the presentation has more equations than needed and may
  contain redundant or conflicting restrictions.
- `redundant`: removing a restriction does not change the represented solution
  object within the active tolerances and rank evidence.
- `inconsistent`: local sections exist, or nearly exist, but cannot be glued
  across declared overlaps.
- `numerically_singular`: the tangent-level restriction or gluing map loses
  rank at the current state.
- `unsupported`: the required context, cover, restriction, or gluing theorem is
  not represented by current contracts.

## Architecture Rules

- Keep the topos layer finite, constructive, and reportable.
- Treat decomposition as cover selection, not as a private solver trick.
- Treat assembly as gluing with explicit overlap checks, not as coordinate
  concatenation.
- Treat gauge fixing as choosing representatives of equivalent sections, not
  as silently deleting degrees of freedom.
- Treat diagnostics as obstruction analysis, not as formatted solver logs.
- Do not let UI, IO, or file paths define contexts, covers, gauges, or
  compatibility rules.

## Practical Boundary

This document does not require a new runtime framework, template hierarchy, or
mathematics dependency. The next architecture step is to add plain data
contracts for `ContextSnapshot`, `CoverPlan`, boundary projections, gluing
reports, and obstruction reports. Those contracts give the system the benefit
of the theory while preserving replaceable engines and readable code.
