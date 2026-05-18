# CDS Module Architecture

## Module Name

**CDS** — Constraint Driven Solver

## Module Purpose

The CDS module is responsible for **parameter solving**: given a set of constraints and initial geometric parameter values, compute the parameter values that satisfy all constraints simultaneously. This is the numerical core of the GCS system.

### Core Responsibilities

1. **Evaluate constraint equations**: Compute residuals (how far each constraint is from being satisfied)
2. **Compute Jacobian matrix**: Partial derivatives of constraint equations with respect to parameters
3. **Iterative solving**: Use Newton-Raphson method to iteratively update parameters until convergence
4. **Convergence detection**: Determine when the solution is sufficiently accurate
5. **Error handling**: Detect and report divergence, singular systems, and inconsistent constraints

## Module Interface

### Header File

```
include/gcs/cds.h
```

### Key Types

```cpp
struct SolverConfig {
    int maxIterations = 100;
    double tolerance = 1e-8;
    double dampingFactor = 1.0;
    bool verbose = false;
};

enum class SolverResult {
    Converged,
    Diverged,
    MaxIterationsReached,
    SingularJacobian,
    InconsistentConstraints
};

struct SolverReport {
    SolverResult result;
    int iterationsUsed;
    double finalResidual;
    std::vector<double> residualHistory;
};
```

### Constraint Equation Interface

```cpp
class IConstraintEquation {
public:
    virtual ~IConstraintEquation() = default;
    virtual int residualCount() const = 0;
    virtual Eigen::VectorXd computeResiduals(const Manager& m) const = 0;
    virtual Eigen::MatrixXd computeJacobian(const Manager& m) const = 0;
};
```

### Primary Interface

```cpp
class ConstraintDrivenSolver {
public:
    explicit ConstraintDrivenSolver(const SolverConfig& config = SolverConfig{});

    SolverReport solve(Manager& m);
    SolverReport solveSubProblem(Manager& m, const SubProblem& sp);

    void setConfig(const SolverConfig& config);
    const SolverConfig& config() const;

private:
    Eigen::VectorXd computeResiduals(const Manager& m, const SubProblem& sp);
    Eigen::MatrixXd computeJacobian(const Manager& m, const SubProblem& sp);
    bool updateParameters(Manager& m, const SubProblem& sp,
                          const Eigen::VectorXd& delta);
    double computeTotalResidual(const Eigen::VectorXd& residuals);

    SolverConfig config_;
};
```

### Usage Example

```cpp
Manager m;
readGraph(m, "input.txt");

DecompositionManager dcm;
auto decomp = dcm.decompose(m);

ConstraintDrivenSolver solver(SolverConfig{.maxIterations = 200, .tolerance = 1e-10});

for (auto& sp : decomp.subProblems) {
    auto report = solver.solveSubProblem(m, sp);
    if (report.result == SolverResult::Converged) {
        std::cout << "Sub-problem " << sp.id << " solved in "
                  << report.iterationsUsed << " iterations\n";
    }
}

Manager solved = dcm.compose(m, decomp.subProblems, ...);
```

## Module Implementation

### Newton-Raphson Algorithm

```
Input: Manager m, SubProblem sp, SolverConfig config
Output: SolverReport

1. Extract parameter vector x from geometries in sp
2. For iteration = 1 to config.maxIterations:
   a. Compute residual vector r = F(x)  — constraint equations evaluated at x
   b. Compute total residual = ||r||
   c. If total residual < config.tolerance:
      return Converged
   d. Compute Jacobian J = ∂F/∂x
   e. Solve linear system: J * Δx = -r  (using LU decomposition)
   f. If J is singular:
      return SingularJacobian
   g. Update parameters: x = x + config.dampingFactor * Δx
   h. If ||Δx|| > divergence_threshold:
      return Diverged
3. Return MaxIterationsReached
```

### Constraint Equation Definitions

Each constraint type defines one or more residual equations:

| Constraint | Residual Equation(s) | Count |
|-----------|----------------------|-------|
| Coincident (Point-Point) | r₁ = x₂-x₁, r₂ = y₂-y₁, r₃ = z₂-z₁ | 3 |
| Parallel (Line-Line) | r₁ = (d₁×d₂)·ê₁, r₂ = (d₁×d₂)·ê₂ | 2 |
| Perpendicular (Line-Line) | r₁ = d₁·d₂ | 1 |
| Distance (Point-Point) | r₁ = ‖p₂-p₁‖ - d_target | 1 |
| Angle (Line-Line) | r₁ = acos(d₁·d₂/(‖d₁‖‖d₂‖)) - θ_target | 1 |

Where:
- `p` = position, `d` = direction vector
- `ê₁, ê₂` = two orthogonal basis vectors perpendicular to d₁

### Jacobian Computation

The Jacobian matrix J has dimensions (m × n) where:
- m = total number of residual equations
- n = total number of free parameters (DOF)

For each residual equation rᵢ and each parameter xⱼ:
```
J[i][j] = ∂rᵢ/∂xⱼ
```

Computed using **analytical derivatives** (not finite differences) for performance and accuracy.

Example for Coincident constraint between points P₁(x₁,y₁,z₁) and P₂(x₂,y₂,z₂):
```
∂r₁/∂x₁ = -1,  ∂r₁/∂x₂ = 1,  ∂r₁/∂y₁ = 0,  ...
∂r₂/∂y₁ = -1,  ∂r₂/∂y₂ = 1,  ∂r₂/∂x₁ = 0,  ...
∂r₃/∂z₁ = -1,  ∂r₃/∂z₂ = 1,  ∂r₃/∂x₁ = 0,  ...
```

### Damped Newton-Raphson

To improve convergence, a damping factor α ∈ (0, 1] is applied:
```
x_new = x + α * Δx
```

Line search can be used to find optimal α:
```
Start with α = 1.0
While ||F(x + α*Δx)|| > ||F(x)||:
    α = α / 2
    If α < α_min: return Diverged
```

## Module Test

### Unit Tests

| Test | Description |
|------|-------------|
| `test_residual_coincident` | Two coincident points: residual = 0 when at same position |
| `test_residual_coincident_nonzero` | Two non-coincident points: residual ≠ 0 |
| `test_residual_parallel` | Two parallel lines: residual = 0 |
| `test_residual_perpendicular` | Two perpendicular lines: residual = 0 |
| `test_residual_distance` | Distance constraint: residual = 0 when distance matches |
| `test_residual_angle` | Angle constraint: residual = 0 when angle matches |
| `test_jacobian_coincident` | Verify Jacobian entries for coincident constraint |
| `test_jacobian_distance` | Verify Jacobian entries for distance constraint |
| `test_solve_simple_distance` | Solve 2 points with distance constraint |
| `test_solve_coincident` | Solve 2 points with coincident constraint |
| `test_solve_well_constrained` | Solve a well-constrained sub-problem |
| `test_solve_under_constrained` | Under-constrained: returns appropriate status |
| `test_solve_over_constrained` | Over-constrained consistent: still converges |
| `test_convergence_report` | Verify SolverReport fields are correct |

### Integration Tests

| Test | Description |
|------|-------------|
| `test_g1_solve` | Solve the g1.txt sample problem |
| `test_decompose_and_solve` | Full pipeline: decompose → solve each sub-problem → compose |
| `test_large_well_constrained` | Solve a generated well-constrained problem with 100 geometries |

### Test Fixtures

- `fixtures/triangles.txt` — 3 points with 3 distance constraints (well-constrained triangle)
- `fixtures/parallel_lines.txt` — 2 lines with parallel constraint
- `fixtures/over_constrained.txt` — Over-constrained but consistent system

## Module Performance

### Complexity Analysis

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Residual evaluation | O(C × K) | C=constraints, K=max residuals per constraint |
| Jacobian computation | O(C × K × D) | D=DOF per geometry |
| LU decomposition | O(D³) | D=total DOF in sub-problem |
| Parameter update | O(D) | Vector addition |
| **Per iteration** | **O(D³)** | Dominated by LU decomposition |
| **Total solve** | **O(I × D³)** | I=iterations to convergence |

### Performance Targets

| Sub-problem Size | DOF | Target Time |
|-----------------|-----|-------------|
| Small (5 geom) | 15-30 | < 1ms |
| Medium (50 geom) | 150-300 | < 100ms |
| Large (500 geom) | 1500-3000 | < 10s |

### Optimization Opportunities

- **Sparse Jacobian**: Most entries are zero; use sparse matrix solver (Eigen::SparseLU)
- **Analytical derivatives**: Already planned; much faster than finite differences
- **Warm starting**: Use previous solution as initial guess for incremental edits
- **Sub-problem parallelism**: Solve independent sub-problems in parallel

## Module Scalability

### Problem Size Scalability

- Dense solver: O(D³) per iteration — practical up to D ≈ 1000
- Sparse solver: O(D¹·⁵) per iteration — practical up to D ≈ 10,000
- Beyond that: need hierarchical decomposition or iterative linear solvers (CG, GMRES)

### Parallelism Opportunities

| Level | Description |
|-------|-------------|
| Sub-problem level | Independent sub-problems solved in parallel (DCM provides this) |
| Jacobian level | Residual and Jacobian computation can be parallelized across constraints |
| Linear solver level | Use parallel LU/QR decomposition (Eigen with MKL) |

## Module Maintainability

### Code Organization

```
include/gcs/cds.h              ← ConstraintDrivenSolver, SolverConfig, SolverReport
src/cds.cpp                     ← Solver implementation
src/cds_equations.cpp           ← Constraint equation implementations (residuals + Jacobians)
```

### Design Patterns

- **Strategy pattern**: IConstraintEquation allows different constraint equation implementations
- **Configuration object**: SolverConfig separates algorithm parameters from solver logic
- **Report object**: SolverReport provides detailed diagnostics without console coupling

### Maintainability Practices

- Constraint equations are isolated in separate source file
- Each constraint type is a self-contained implementation
- Solver algorithm is independent of specific constraint types
- No console output from solver — results returned via SolverReport

## Module Extensibility

### Adding a New Constraint Type

1. Implement residual equations for the new constraint type
2. Implement Jacobian entries for the new constraint type
3. Register the new constraint equation in the solver's equation factory
4. No changes to the Newton-Raphson algorithm itself

### Alternative Solver Algorithms

| Algorithm | When to Use |
|-----------|-------------|
| Newton-Raphson | Well-constrained, good initial guess |
| Levenberg-Marquardt | Over-constrained least-squares problems |
| BFGS | Under-constrained optimization |
| Genetic algorithm | No good initial guess, global search |

The IConstraintEquation interface allows swapping solver algorithms without rewriting constraint equations.

### Extension Points

| Extension | Mechanism |
|-----------|-----------|
| New constraint type | Implement IConstraintEquation |
| Different solver algorithm | Subclass or replace ConstraintDrivenSolver |
| Custom convergence criteria | Override convergence check in SolverConfig |
| External linear algebra | Replace Eigen with custom matrix library |

## Module Reusability

### Reuse Scenarios

| Scenario | How CDS Supports It |
|----------|-------------------|
| Different geometry types | IConstraintEquation abstracts over geometry types |
| Different solver algorithms | SolverConfig and IConstraintEquation are algorithm-agnostic |
| Real-time solving | SolverReport provides timing data; can be profiled and optimized |
| Batch solving | Multiple Managers can be solved independently |
| Embedded solver | CDS has no IO or UI dependencies; can be used as a library |

### Reusability Principles

- CDS depends on Core and LGS only — no IO dependency
- IConstraintEquation provides a clean extension point
- SolverConfig allows tuning without code changes
- No global state or singletons
- No file I/O or console output
