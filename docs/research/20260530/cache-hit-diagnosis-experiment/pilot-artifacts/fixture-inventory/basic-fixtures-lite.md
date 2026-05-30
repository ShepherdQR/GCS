# Basic Fixture Inventory - Lite

Run: `CACHE_HIT_EXPERIMENT_RUN fixture-inventory-1-lite fixture-inventory-1 Lite`

Controller task card: `docs/agentic/tasks/2026-05-31-cache-hit-pilot-eight-pairs.md`

Scope: `fixtures/scene/basic`

## Summary

- File count: 2 files found by `Get-ChildItem`; 1 file found by `rg --files`.
- Primary fixture: `g1.txt`, a legacy text scene with 3 groups, 5 geometric entries, 2 constraints, state rows, and 2 scalar values.
- Companion signal: `g1_graph.txt` has the same apparent topology and constraint rows as `g1.txt`, but integer-valued state rows. It is not reported by `rg --files`, suggesting an ignored or stale companion artifact rather than a normal tracked fixture candidate.
- Malformed signals: none observed from direct read; both files are non-empty and follow the same coarse block pattern.
- Stale/readiness signals: `g1_graph.txt` should be treated as lower readiness until its purpose is confirmed, because the normal repository file listing excluded it.

## Command Evidence

```powershell
rg --files fixtures\scene\basic
# fixtures\scene\basic\g1.txt
```

```powershell
Get-ChildItem -File fixtures\scene\basic | Select-Object Name,Length,LastWriteTime
# g1.txt        212 bytes
# g1_graph.txt  164 bytes
```

```powershell
Get-Content fixtures\scene\basic\g1.txt
# starts with: 3 / 0 1 2 / 5
# includes 2 constraint rows and scalar values: 0 0.0, 1 1.5
```

```powershell
Get-Content fixtures\scene\basic\g1_graph.txt
# same leading group/topology pattern as g1.txt
# state/value rows use integer-style values
```

```powershell
git check-ignore -v fixtures\scene\basic\g1_graph.txt
# exit code 1; no ignore rule printed
# warning: unable to access 'C:\Users\QR/.config/git/ignore': Permission denied
```
