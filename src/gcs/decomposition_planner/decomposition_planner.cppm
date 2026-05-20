module;

#include <vector>

export module gcs.decomposition_planner;

export import gcs.kernel;
export import gcs.incidence_graph;

export namespace gcs::planning {

struct PlannerInput {
    ModelSnapshot model;
    graph::IncidenceIndices incidence;
    SolveIntent solveIntent;
    std::vector<StageReport> diagnosticHints;
};

struct Subproblem {
    int id = 0;
    ContextId contextId;
    std::vector<EntityId> activeVariables;
    std::vector<ConstraintId> activeEquations;
    std::vector<EntityId> boundaryVariables;
    int expectedFreeDof = 0;
};

struct SolveStep {
    int order = 0;
    ContextId contextId;
};

struct PlannerOutput {
    CoverPlan coverPlan;
    std::vector<ContextSnapshot> overlapContexts;
    std::vector<BoundaryProjection> boundaryProjections;
    std::vector<Subproblem> subproblems;
    std::vector<SolveStep> solveOrder;
    GaugePolicy gaugePolicy;
    StageReport structuralReport;
};

PlannerOutput planDecomposition(const PlannerInput& input);

}
