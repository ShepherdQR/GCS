module;

#include <string>
#include <vector>

export module gcs.cds;

export import gcs.core;
export import gcs.dcm;

export namespace gcs::cds {

struct SolverConfig {
    int maxIterations = 100;
    double tolerance = 1e-8;
    double dampingFactor = 1.0;
    SolveMode mode = SolveMode::Update;
    bool verbose = false;
};

enum class SolverResult {
    Converged,
    Diverged,
    MaxIterationsReached,
    SingularJacobian,
    InconsistentConstraints
};

std::string toString(SolverResult result);

struct SolverReport {
    SolverResult result = SolverResult::Converged;
    int iterationsUsed = 0;
    double initialResidual = 0.0;
    double finalResidual = 0.0;
};

class ConstraintDrivenSolver {
public:
    explicit ConstraintDrivenSolver(const SolverConfig& config = SolverConfig{});

    SolverReport solve(Manager& m);
    SolverReport solveSubProblem(Manager& m, const dcm::SubProblem& sp);

    void setConfig(const SolverConfig& config);
    const SolverConfig& config() const;

private:
    SolverConfig config_;
};

}
