---
name: gcs-io-adapter-steward
description: IO adapter design and review for GCS. Invoke when work touches scene schemas, JSON or text serialization, schema registry, migrations, canonical output, parse errors, validation reports, fixture compatibility, round-trip diffs, or canonical digests.
---

# GCS IO Adapter Steward

## Start Here

Use this skill for `gcs.io_adapters` target design. IO preserves solver truth
across boundaries; it does not own mathematical meaning.

Read:

- `docs/architecture/62-module-agents.md` -> `IO Adapter Agent`
- `docs/architecture/63-target-contract-interface-implementation-test-design.md`
  -> `IO Adapters Target Design`
- `docs/architecture/50-implementation/third-party-policy.md`

## Workflow

1. Define schema version, format, compatibility mode, units, and tolerance
   handling.
2. Use explicit scene load, write, normalize, migration, and round-trip request
   contracts.
3. Report every parse, validation, and meaning-changing migration event.
4. Preserve deterministic canonical serialization and stable IDs.
5. Name tests for schema loading, rejected invalid input, migration, byte
   determinism, load-write-load equality, and round-trip diffs.

## Own

- Scene schema registry.
- Canonical text and JSON serialization.
- Migration reports, typed parse errors, round-trip diffs, canonical digests.

## Refuse

- Lower solver imports from IO.
- Hidden schema repair.
- Non-deterministic output.

## Required Output

Return a structured design report with:

- schema and migration impact;
- typed IO contracts;
- canonicalization rules;
- compatibility risks;
- required fixtures and tests;
- handoffs to kernel or quality.

## Claude Code Integration

When invoked for IO adapter work:
- Use `Read` on architecture docs and existing IO code before modifying schemas.
- Use `Grep` to find all serializers and deserializers affected by a schema
  change before editing.
- When adding a new field, verify it round-trips through both C++ and Python
  paths via `Bash` commands.
- Use `Edit` for schema changes; keep field order deterministic.
- For migration work, `Grep` for all fixtures that exercise the old schema
  version and verify they still load after migration.
