#pragma once

#include "core/core.h"
#include "lgs/lgs.h"
#include "dcm/dcm.h"
#include <vector>
#include <string>

namespace gcs {
namespace cds {

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

std::string toString(SolverResult result);

struct SolverReport {
    SolverResult result;
    int iterationsUsed;
    double initialResidual;
    double finalResidual;
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
}
