# LGS Module Architecture

## Module Name

**LGS** — Local Geometric Solver

## Module Purpose

The LGS module is responsible for **status solving**: analyzing a constraint system to determine its constraint status — whether it is well-constrained, under-constrained, or over-constrained. This analysis is critical for:

1. **Diagnosing problems** before attempting to solve — telling the user what's wrong
2. **Guiding the solver** — under-constrained systems need different handling than well-constrained ones
3. **Validating solutions** — after solving, verifying that all constraints are satisfied

### Core Responsibilities

1. **DOF (Degree of Freedom) analysis**: Count the total DOF in a sub-problem and how many are removed by constraints
2. **Constraint status classification**: Classify each sub-problem as well/over/under-constrained
3. **Consistency checking**: For over-constrained systems, determine if redundant constraints are consistent
4. **Constraint satisfaction verification**: After solving, check how well constraints are satisfied

## Module Interface

### Header File

```
include/gcs/lgs.h
```

### Key Types

```cpp
enum class ConstraintStatus {
    WellConstrained,
    UnderConstrained,
    OverConstrained,
    OverConstrainedConsistent
};

struct DOFAnalysis {
    int geometryDOF;
    int constraintRemovedDOF;
    int netDOF;
    ConstraintStatus status;
};

struct ConstraintViolation {
    int constraintId;
    double residual;
    double tolerance;
    bool satisfied;
};

struct StatusReport {
    ConstraintStatus overallStatus;
    DOFAnalysis dofAnalysis;
    std::vector<ConstraintViolation> violations;
    bool isConsistent;
    std::string summaryText;
};
```

### Primary Interface

```cpp
class LocalGeometricSolver {
public:
    LocalGeometricSolver() = default;

    DOFAnalysis analyzeDOF(const Manager& m) const;
    DOFAnalysis analyzeDOF(const Manager& m, const SubProblem& sp) const;

    StatusReport analyzeStatus(const Manager& m) const;
    StatusReport analyzeStatus(const Manager& m, const SubProblem& sp) const;

    std::vector<ConstraintViolation> checkSatisfaction(
        const Manager& m,
        double tolerance = 1e-6) const;

    bool isWellConstrained(const Manager& m) const;
    bool isUnderConstrained(const Manager& m) const;
    bool isOverConstrained(const Manager& m) const;

private:
    int computeGeometryDOF(const Manager& m, const SubProblem& sp) const;
    int computeConstraintRemovedDOF(const Manager& m, const SubProblem& sp) const;
    ConstraintStatus classifyStatus(int netDOF, int constraintCount, int geometryCount) const;
    double computeConstraintResidual(const Manager& m, const Constraint& c) const;
};
```

### Usage Example

```cpp
Manager m;
readGraph(m, "input.txt");

DecompositionManager dcm;
auto decomp = dcm.decompose(m);

LocalGeometricSolver lgs;
for (const auto& sp : decomp.subProblems) {
    auto report = lgs.analyzeStatus(m, sp);
    std::cout << "Sub-problem " << sp.id
              << ": " << report.dofAnalysis.netDOF << " DOF, "
              << statusToString(report.overallStatus) << "\n";
}

auto globalReport = lgs.analyzeStatus(m);
if (globalReport.overallStatus == ConstraintStatus::WellConstrained) {
    ConstraintDrivenSolver cds;
    cds.solve(m);
}
```

## Module Implementation

### DOF Analysis Algorithm

Each geometry type contributes a fixed number of DOF:

| Geometry Type | DOF | Parameters |
|--------------|-----|------------|
| Point | 3 | x, y, z |
| Line | 6 | x₁, y₁, z₁, x₂, y₂, z₂ |
| Plane | 6 | x, y, z, nx, ny, nz |

Each constraint type removes a fixed number of DOF:

| Constraint Type | DOF Removed | Notes |
|----------------|-------------|-------|
| Coincident | 3 | Forces 3 position parameters to match |
| Parallel | 2 | Removes 2 rotational DOF |
| Perpendicular | 1 | Removes 1 rotational DOF |
| Distance | 1 | Removes 1 positional DOF |
| Angle | 1 | Removes 1 rotational DOF |

**Net DOF calculation:**
```
netDOF = Σ(geometryDOF) - Σ(constraintRemovedDOF)
```

**Important**: Rigid sets affect DOF counting. When geometries are in the same RigidSet, they share DOF — the rigid set moves as one unit. The effective DOF of a RigidSet is 6 (3 translational + 3 rotational), regardless of how many geometries it contains.

**RigidSet-aware DOF calculation:**
```
effectiveGeometryDOF = Σ(rigidSetDOF)  // 6 per rigid set, not per geometry
constraintRemovedDOF = Σ(constraintRemovedDOF)  // same as before
netDOF = effectiveGeometryDOF - constraintRemovedDOF
```

### Status Classification

```
if (netDOF == 0):
    status = WellConstrained
elif (netDOF > 0):
    status = UnderConstrained
elif (netDOF < 0):
    // Over-constrained, but may be consistent
    if (redundantConstraintsAreConsistent):
        status = OverConstrainedConsistent
    else:
        status = OverConstrained
```

### Consistency Checking

For over-constrained systems, we need to check if the redundant constraints are consistent with each other. This is done by:

1. **Rank analysis**: Compute the rank of the Jacobian matrix
2. **If rank < number of constraints**: Some constraints are linearly dependent
3. **If dependent constraints are consistent**: The system has a solution despite being over-constrained
4. **If dependent constraints are inconsistent**: The system has no solution

### Constraint Residual Computation

Each constraint type has a residual function that measures how far it is from being satisfied:

| Constraint | Residual Function |
|-----------|------------------|
| Coincident | ‖p₂ - p₁‖ |
| Parallel | ‖d₁ × d₂‖ |
| Perpendicular | d₁ · d₂ |
| Distance | ‖p₂ - p₁‖ - d_target |
| Angle | acos(d₁·d₂/(‖d₁‖‖d₂‖)) - θ_target |

## Module Test

### Unit Tests

| Test | Description |
|------|-------------|
| `test_dof_single_point` | 1 Point → 3 DOF |
| `test_dof_single_line` | 1 Line → 6 DOF |
| `test_dof_single_plane` | 1 Plane → 6 DOF |
| `test_dof_point_with_distance` | 2 Points + Distance → 3+3-1 = 5 DOF |
| `test_dof_coincident_points` | 2 Points + Coincident → 3+3-3 = 3 DOF |
| `test_well_constrained_triangle` | 3 Points + 3 Distances → 3+3+3-1-1-1 = 6 DOF (without rigid set) |
| `test_under_constrained` | 2 Points, 0 constraints → under-constrained |
| `test_over_constrained` | 2 Points + Coincident + Distance → over-constrained |
| `test_rigid_set_dof` | RigidSet with 2 Points → 6 DOF (not 3+3=6, same result but conceptually different) |
| `test_residual_coincident_satisfied` | Two coincident points → residual = 0 |
| `test_residual_coincident_violated` | Two non-coincident points → residual > 0 |
| `test_residual_distance_satisfied` | Points at correct distance → residual = 0 |
| `test_residual_distance_violated` | Points at wrong distance → residual ≠ 0 |
| `test_status_report_text` | Verify summary text generation |
| `test_check_satisfaction_all` | All constraints satisfied → no violations |
| `test_check_satisfaction_some` | Some constraints violated → violations reported |

### Integration Tests

| Test | Description |
|------|-------------|
| `test_lgs_after_dcm` | Analyze each sub-problem from DCM decomposition |
| `test_lgs_before_after_solve` | Status changes from under-constrained to well-constrained after solving |

## Module Performance

### Complexity Analysis

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| DOF counting | O(G + C) | G=geometries, C=constraints — simple summation |
| Status classification | O(1) | Based on net DOF value |
| Consistency checking | O(C × D²) | Requires Jacobian rank analysis |
| Residual computation | O(C × K) | K=max geometryIds per constraint |
| Full status report | O(C × D²) | Dominated by consistency check |

### Performance Targets

| Sub-problem Size | DOF Analysis | Full Status Report |
|-----------------|-------------|-------------------|
| Small (5 geom) | < 0.1ms | < 1ms |
| Medium (50 geom) | < 0.5ms | < 10ms |
| Large (500 geom) | < 5ms | < 100ms |

### Optimization Notes

- DOF counting is extremely fast — just integer arithmetic
- Consistency checking is expensive but only needed for over-constrained systems
- Residual computation is shared with CDS module — avoid duplication

## Module Scalability

### Problem Size Scalability

- DOF analysis scales linearly — O(G + C)
- Consistency checking scales polynomially — O(C × D²)
- For very large problems, consistency checking can be done per sub-problem (after DCM decomposition)

### Scalability Strategy

- DOF analysis is always fast — no scalability concerns
- Consistency checking can be skipped for well-constrained and under-constrained systems
- For large over-constrained systems, use iterative rank estimation instead of full SVD

## Module Maintainability

### Code Organization

```
include/gcs/lgs.h              ← LocalGeometricSolver, DOFAnalysis, StatusReport
src/lgs.cpp                     ← DOF analysis, status classification
src/lgs_residuals.cpp           ← Constraint residual computation (shared pattern with CDS)
```

### Design Decisions

| Decision | Rationale |
|----------|-----------|
| Separate DOF analysis from status report | DOF is cheap; full report is expensive; callers choose granularity |
| RigidSet-aware DOF counting | Correct DOF counting requires understanding rigid body mechanics |
| Shared residual computation | Same residual functions needed by LGS (checking) and CDS (solving) |
| Status enum not boolean | Four states provide more information than a simple yes/no |

### Maintainability Practices

- DOF values are defined in one place (per geometry/constraint type)
- Residual functions follow a consistent pattern
- No console output — results returned via StatusReport
- Clear separation between analysis and reporting

## Module Extensibility

### Adding a New Geometry Type

1. Add DOF value for the new geometry type (e.g., Circle = 5 DOF)
2. Update `computeGeometryDOF()` to handle the new type
3. No changes to constraint analysis

### Adding a New Constraint Type

1. Add DOF-removed value for the new constraint type
2. Add residual computation for the new constraint type
3. Update `computeConstraintRemovedDOF()` to handle the new type
4. Update `computeConstraintResidual()` to handle the new type

### Extension Points

| Extension | Mechanism |
|-----------|-----------|
| New geometry DOF | Add case to computeGeometryDOF() |
| New constraint DOF | Add case to computeConstraintRemovedDOF() |
| New constraint residual | Add case to computeConstraintResidual() |
| Custom status classification | Override classifyStatus() |
| Different consistency algorithms | Strategy pattern for consistency checker |

## Module Reusability

### Reuse Scenarios

| Scenario | How LGS Supports It |
|----------|-------------------|
| Pre-solve validation | analyzeStatus() called before CDS.solve() |
| Post-solve verification | checkSatisfaction() called after solving |
| Interactive constraint editing | Quick DOF feedback as user adds/removes constraints |
| CAD constraint diagnostics | StatusReport provides human-readable diagnostics |
| Constraint system design | DOF analysis helps designers create well-constrained systems |

### Reusability Principles

- LGS depends only on Core — no dependency on CDS or DCM
- DOF analysis is a pure function of the data model
- Residual computation is shared with CDS (common interface)
- No file I/O or console output
- No global state
