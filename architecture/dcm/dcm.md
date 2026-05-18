# DCM Module Architecture

## Module Name

**DCM** — Decomposition Manager

## Module Purpose

The DCM module is responsible for **problem decomposition and composition**: breaking down a large constraint graph into smaller, independently solvable sub-problems, and re-assembling the solved sub-problems back into a complete solution.

### Why Decomposition Matters

A large constraint graph (e.g., 10,000 geometries) is expensive to solve as a single system. However, real-world constraint graphs often contain **independent clusters** — groups of geometries connected by constraints within the group but not to geometries outside the group. These clusters can be solved independently, reducing an O(n³) problem to multiple O(k³) problems where k << n.

### Core Responsibilities

1. **Decompose**: Split the constraint graph into connected components (sub-problems)
2. **Compose**: Merge solved sub-problems back into the complete Manager
3. **Validate**: Ensure decomposition preserves constraint integrity

## Module Interface

### Header File

```
include/gcs/dcm.h
```

### Key Types

```cpp
enum class SolveStatus {
    WellConstrained,
    UnderConstrained,
    OverConstrained,
    OverConstrainedConsistent
};

struct SubProblem {
    int id;
    std::vector<int> geometryIds;
    std::vector<int> constraintIds;
    std::vector<int> rigidSetIds;
    SolveStatus status = SolveStatus::UnderConstrained;
};

struct DecompositionResult {
    std::vector<SubProblem> subProblems;
    int totalGeometries;
    int totalConstraints;
    bool isSingleComponent;
};
```

### Primary Interface

```cpp
class DecompositionManager {
public:
    DecompositionManager() = default;

    DecompositionResult decompose(const Manager& m);

    Manager compose(const Manager& original,
                    const std::vector<SubProblem>& solvedSubProblems,
                    const std::vector<Manager>& solvedManagers);

    SubProblem extractSubProblem(const Manager& m,
                                 const std::vector<int>& geometryIds) const;

private:
    void buildAdjacencyList(const Manager& m);
    std::vector<std::vector<int>> findConnectedComponents();
    std::vector<int> bfsComponent(int startGeomId,
                                   const std::unordered_map<int, std::vector<int>>& adj);

    std::unordered_map<int, std::vector<int>> adjacencyList_;
    std::unordered_set<int> visited_;
};
```

### Usage Example

```cpp
Manager m;
readGraph(m, "input.txt");

DecompositionManager dcm;
DecompositionResult result = dcm.decompose(m);

std::cout << "Decomposed into " << result.subProblems.size() << " sub-problems\n";
for (const auto& sp : result.subProblems) {
    std::cout << "  Sub-problem " << sp.id
              << ": " << sp.geometryIds.size() << " geometries, "
              << sp.constraintIds.size() << " constraints\n";
}
```

## Module Implementation

### Decomposition Algorithm

The decomposition uses **connected-component analysis** on the constraint graph:

```
Step 1: Build adjacency list
  For each constraint C connecting geometries G1, G2, ..., Gk:
    Add edges: G1↔G2, G1↔G3, ..., G1↔Gk (all pairs)
    Also: for each geometry Gi, add edge Gi↔RigidSet(Gi)
      (geometries in the same RigidSet are connected)

Step 2: Find connected components using BFS/DFS
  Start from each unvisited geometry
  BFS/DFS to find all reachable geometries
  Each connected component = one SubProblem

Step 3: Assign constraints to sub-problems
  For each constraint:
    All its geometryIds must belong to the same component
    (If not, the constraint spans components — this is an error or requires special handling)

Step 4: Assign rigid sets to sub-problems
  A rigid set belongs to the sub-problem of its geometries
```

### Composition Algorithm

```
Step 1: For each solved SubProblem, extract the solved parameter values
Step 2: Create a new Manager with the original topology
Step 3: Copy solved parameter values from each SubProblem into the new Manager
Step 4: Verify all constraints are satisfied (optional validation step)
```

### Edge Cases

| Case | Handling |
|------|----------|
| Single component (no decomposition possible) | Return single SubProblem with all geometries |
| Isolated geometry (no constraints) | Each isolated geometry is its own sub-problem |
| Constraint spanning rigid sets | Rigid set connectivity ensures they're in the same component |
| Empty Manager | Return empty DecompositionResult |

## Module Test

### Unit Tests

| Test | Description |
|------|-------------|
| `test_empty_manager` | Decompose empty Manager → 0 sub-problems |
| `test_single_geometry` | Decompose Manager with 1 geometry, 0 constraints → 1 sub-problem |
| `test_two_disconnected` | 2 geometries, 0 constraints → 2 sub-problems |
| `test_two_connected` | 2 geometries, 1 constraint → 1 sub-problem |
| `test_chain` | 5 geometries in a chain → 1 sub-problem |
| `test_two_components` | 2 pairs of connected geometries → 2 sub-problems |
| `test_rigid_set_grouping` | Geometries in same RigidSet are in same component |
| `test_compose_identity` | Decompose → Compose → original Manager |
| `test_compose_preserves_topology` | Topology unchanged after decompose+compose |
| `test_g1_sample` | Decompose g1.txt → verify expected sub-problem structure |

### Integration Tests

| Test | Description |
|------|-------------|
| `test_decompose_solve_compose` | Full pipeline: decompose → solve → compose → verify |
| `test_large_graph` | Decompose graph with 1000 geometries, verify correctness |

## Module Performance

### Complexity Analysis

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Build adjacency list | O(C × K) | C=constraints, K=max geometryIds per constraint |
| BFS per component | O(V + E) | V=geometries, E=adjacency edges |
| Full decomposition | O(V + E) | Linear in graph size |
| Composition | O(V) | Copy parameter values |

### Performance Targets

| Graph Size | Geometries | Decomposition Time |
|-----------|-----------|-------------------|
| Small | 100 | < 1ms |
| Medium | 10,000 | < 10ms |
| Large | 1,000,000 | < 1s |

### Memory Usage

- Adjacency list: O(V + E) — typically O(V) for sparse graphs
- Visited set: O(V)
- Sub-problem vectors: O(V) total
- Overall: O(V + E) — linear in graph size

## Module Scalability

### Graph Size Scalability

- BFS/DFS is O(V+E) — scales linearly with graph size
- No recursive algorithms — uses iterative BFS to avoid stack overflow on large graphs
- Adjacency list representation is memory-efficient for sparse graphs

### Parallel Decomposition

- Connected components can be found in parallel using union-find
- Each sub-problem can be solved independently in parallel after decomposition
- Composition is embarrassingly parallel — each sub-problem's results are independent

### Scalability Limits

| Limit | Value | Mitigation |
|-------|-------|-----------|
| Max geometries | ~10M | Use 64-bit IDs if needed |
| Max constraints | ~10M | Use 64-bit IDs if needed |
| Max components | ~10M | No practical limit |

## Module Maintainability

### Code Organization

```
include/gcs/dcm.h    ← DecompositionManager class, SubProblem, DecompositionResult
src/dcm.cpp          ← Implementation
```

### Design Patterns

- **Strategy pattern**: Decomposition algorithm can be swapped (BFS vs Union-Find)
- **Value objects**: SubProblem and DecompositionResult are immutable after creation
- **No side effects**: decompose() does not modify the input Manager

### Maintainability Practices

- Clear separation between graph construction and traversal
- Well-named methods: `buildAdjacencyList`, `findConnectedComponents`, `bfsComponent`
- All edge cases explicitly handled and tested
- No global state

## Module Extensibility

### Extension Points

| Extension | How to Add |
|-----------|-----------|
| Different decomposition strategy | Subclass DecompositionManager or use strategy pattern |
| Hierarchical decomposition | Decompose recursively — each sub-problem can be further decomposed |
| Constraint-aware decomposition | Consider constraint types when splitting (e.g., keep distance constraints together) |
| Incremental decomposition | Support adding/removing geometries without full re-decomposition |

### Future Extensions

- **Cluster decomposition**: Beyond connected components, use spectral clustering or constraint-weighted graph partitioning
- **Hierarchical decomposition**: Multi-level decomposition for very large graphs
- **Incremental updates**: Re-decompose only the affected sub-problem when a constraint is added/removed

## Module Reusability

### Reuse Scenarios

| Scenario | How DCM Supports It |
|----------|-------------------|
| Different solver backends | DCM output (SubProblem) is solver-agnostic |
| Parallel solving | Each SubProblem is independent; can be dispatched to different threads/machines |
| Problem visualization | SubProblem IDs can be used to color-code the visualization |
| Incremental editing | Decomposition can be re-run after graph modifications |
| Other graph problems | DecompositionManager can decompose any graph represented as Manager |

### Reusability Principles

- DCM depends only on Core — no dependency on IO, LGS, or CDS
- SubProblem is a self-contained data structure
- No file I/O or console output in DCM
- No global state or singletons
