module;

#include <string>
#include <vector>

export module gcs.decomposition_planner;

export import gcs.kernel;
export import gcs.incidence_graph;

export namespace gcs::planning {

using gcs::kernel::BoundaryProjection;
using gcs::kernel::ConstraintId;
using gcs::kernel::ContextId;
using gcs::kernel::ContextSnapshot;
using gcs::kernel::CoverPlan;
using gcs::kernel::EntityId;
using gcs::kernel::GaugePolicy;
using gcs::kernel::ModelSnapshot;
using gcs::kernel::ReportMessage;
using gcs::kernel::SolveIntent;
using gcs::kernel::StageReport;

struct PlannerInput {
    ModelSnapshot model;
    graph::IncidenceIndices incidence;
    SolveIntent solve_intent;
    std::vector<StageReport> diagnostic_hints;
};

struct Subproblem {
    int id = 0;
    ContextId context_id;
    std::vector<EntityId> active_variables;
    std::vector<ConstraintId> active_equations;
    std::vector<EntityId> boundary_variables;
    int expected_free_dof = 0;
};

struct SolveStep {
    int order = 0;
    ContextId context_id;
};

struct UnsupportedPlanReport {
    bool unsupported = false;
    std::string code;
    std::string message;
};

struct PlannerOutput {
    CoverPlan cover_plan;
    std::vector<ContextSnapshot> overlap_contexts;
    std::vector<BoundaryProjection> boundary_projections;
    std::vector<Subproblem> subproblems;
    std::vector<SolveStep> solve_order;
    GaugePolicy gauge_policy;
    StageReport structural_report;
    UnsupportedPlanReport unsupported_report;
};

struct CoverValidationReport {
    bool valid = true;
    bool covers_all_entities = true;
    bool covers_all_constraints = true;
    bool contexts_reference_known_ids = true;
    bool boundary_projections_reference_known_contexts = true;
    int context_count = 0;
    int boundary_projection_count = 0;
    std::vector<ReportMessage> messages;
};

struct SolveOrderValidationReport {
    bool valid = true;
    bool strictly_ordered = true;
    bool every_step_has_context = true;
    bool covers_all_subproblems = true;
    int step_count = 0;
    std::vector<ReportMessage> messages;
};

PlannerOutput plan_decomposition(const PlannerInput& input);
gcs::kernel::ContractResult<CoverValidationReport> validate_cover(
    const ModelSnapshot& model,
    const CoverPlan& cover_plan);
gcs::kernel::ContractResult<SolveOrderValidationReport> validate_solve_order(
    const PlannerOutput& output);

}
