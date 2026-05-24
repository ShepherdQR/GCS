# Domain Contracts

## Stable Identity

Every durable object has a stable ID:

- entity ID;
- constraint ID;
- rigid set or group ID;
- solve command ID;
- state version ID;
- report ID.
- context ID for decomposition snapshots;
- cover ID for planned local-to-global solves.

Coordinates may change. IDs do not change unless the user performs an explicit
topology edit.

## Core Types

The target kernel should model:

- geometric entities;
- constraints;
- groups and rigid sets;
- parameter blocks;
- units and dimensions;
- tolerance policy;
- solve intent;
- state versions;
- context snapshots and boundary references;
- references between objects.

## Context And Boundary Identity

Decomposition introduces local views of the same durable model. These views
must preserve identity rather than cloning domain truth:

- a `ContextSnapshot` references stable entity and constraint IDs from a model
  snapshot;
- a boundary variable references the same durable entity or parameter block
  seen through a smaller overlap context;
- a `CoverPlan` has stable IDs for contexts, overlaps, and projections;
- local solve proposals identify the context they were computed over;
- gluing reports identify every overlap they accepted or rejected.

Context identity is solver/runtime metadata. It must not replace durable entity
or constraint identity.

## Model Immutability Boundary

The durable model should be treated as immutable inside a solve. Solvers receive
snapshots and return proposed deltas or proposed states. Runtime transactions
commit or reject those proposals.

## Constraint Semantics

A constraint definition should declare:

- supported entity signatures;
- parameter schema;
- residual dimension;
- generic DOF effect when known;
- residual evaluator;
- Jacobian provider or differentiation strategy;
- degeneracy warnings;
- display and serialization names.

This belongs in `constraint_catalog`, not inside arbitrary solver branches.

## Rigid Set Incidence

Rigid sets are the body-level incidence boundary for persisted scenes. A
constraint may reference multiple geometries, but every referenced geometry must
belong to a different rigid set. Constraints inside a single rigid set are
invalid model data because rigid-set-internal geometry is already treated as
belonging to the same body-level parameter block.

Scene IO, fixture generation, repair tools, and GUI construction flows should
reject or repair same-rigid-set constraint endpoints before the model reaches a
solver run. Legacy fixtures that intentionally exercise malformed input should
name that intent explicitly instead of appearing as normal saved models.

## Serialization Contract

Scenes and fixtures should be versioned. A serialized model should identify:

- schema version;
- units;
- tolerance policy when non-default;
- entities and parameter values;
- constraints and parameters;
- groups or rigid sets;
- behavior intent when the scene is meant to be solved, replayed, or used as a
  public demo.

Serialization must round-trip stable IDs and produce deterministic output.
For `gcs-0.3` JSON, the scene-facing `behavior` object maps to
`ModelSnapshot.solve_intent`: `mode`, `fixed_geometry_ids`,
`driven_geometry_ids`, and `target_constraint_ids` are solver inputs, not
viewer annotations. Loaders must reject behavior references that do not resolve
to stable entity or constraint IDs in the same scene.
