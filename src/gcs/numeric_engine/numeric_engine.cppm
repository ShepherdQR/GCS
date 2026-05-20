module;

#include <string>
#include <vector>

export module gcs.numeric_engine;

export import gcs.kernel;
export import gcs.constraint_catalog;

export namespace gcs::numeric {

struct SolveLimits {
    int maxIterations = 25;
    double trustRegionRadius = 1.0;
};

struct NumericTask {
    ModelSnapshot problemSnapshot;
    ContextSnapshot contextSnapshot;
    std::vector<EntityId> activeVariables;
    std::vector<ConstraintId> activeEquations;
    std::vector<EntityId> boundaryVariables;
    std::string parameterization = "default-manifold-retraction";
    TolerancePolicy tolerances;
    GaugePolicy gaugePolicy;
    SolveLimits solveLimits;
};

struct NumericReport {
    SolveStatus resultCode = SolveStatus::NotRun;
    LocalSection localSection;
    ProposedState proposedState;
    double initialResidual = 0.0;
    double finalResidual = 0.0;
    double stepNorm = 0.0;
    int rankEstimate = 0;
    double conditionEstimate = 0.0;
    int iterationCount = 0;
    std::string failureCause;
    StageReport stageReport;
};

NumericTask makeNumericTask(const ModelSnapshot& model,
                            const ContextSnapshot& context,
                            const std::vector<EntityId>& activeVariables,
                            const std::vector<ConstraintId>& activeEquations,
                            const GaugePolicy& gaugePolicy);

NumericReport solveLocal(const NumericTask& task);

}
