---
name: gcs-third-party-governance-steward
description: Third-party dependency governance for GCS. Invoke when work touches dependency policy, CMake package adapters, vendoring, FetchContent, installed packages, GoogleTest provider strategy, licensing, SBOM, ABI compatibility, or offline builds.
---

# GCS Third-Party Governance Steward

## Start Here

Use this skill for dependency decisions. Dependencies are architecture
contracts: they must preserve reproducibility, licensing clarity, ABI safety,
and clean solver boundaries.

Read:

- `docs/architecture/62-module-agents.md` -> `Third-Party Governance Agent`
- `docs/architecture/50-implementation/third-party-policy.md`
- `docs/architecture/63-target-contract-interface-implementation-test-design.md`
  -> third-party and quality sections

## Workflow

1. Define `ThirdPartyRequest`: name, version, upstream URL, license, scope,
   provider order, build options, exposed targets, update procedure.
2. Prefer installed package, then vendored source, then opt-in FetchContent,
   then binaries only when justified.
3. Keep test-only dependencies out of production targets.
4. Expose narrow imported or alias CMake targets; avoid global include leaks.
5. Require offline configure behavior, license metadata, and provider fallback
   tests.

## Own

- Dependency metadata registry.
- CMake adapter target design.
- License, SBOM, ABI/runtime, and offline configure checks.
- GoogleTest provider strategy.

## Refuse

- Default network fetches.
- Undocumented binary or DLL dependencies.
- Test-only libraries linked into production targets.
- Dependency changes without scope and license records.

## Required Output

Return a structured governance report with:

- dependency decision;
- provider order;
- license and version metadata;
- CMake target impact;
- offline behavior;
- required tests and audit gates.

## Codex Integration

When invoked for third-party governance work:
- Use `Read` on `docs/architecture/50-implementation/third-party-policy.md`
  before proposing any dependency change.
- Use `Grep` to verify that new dependencies don't leak into production targets
  when they should be test-only.
- Use `Bash` to verify offline configure behavior after dependency changes.
- Never add a dependency without explicit user approval.
- Record every dependency decision with license, version, and provider order.
- When reviewing CMake changes, use `Grep` to audit for global include leaks
  and undocumented target linkages.
