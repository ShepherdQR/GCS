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
using gcs::kernel::ProjectionId;
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

struct SolveDagNode {
    ContextId context_id;
    int topological_order = 0;
    bool solved_locally = true;
    bool aggregation_context = false;
};

struct SolveDagEdge {
    ContextId source_context_id;
    ContextId target_context_id;
    ProjectionId projection_id;
    std::vector<EntityId> boundary_entity_ids;
    std::vector<ConstraintId> boundary_constraint_ids;
};

struct SolveDag {
    std::vector<SolveDagNode> nodes;
    std::vector<SolveDagEdge> edges;
};

struct UnsupportedPlanReport {
    bool unsupported = false;
    std::string code;
    std::string message;
};

// --- Spanning tree plan ---

struct SpanningTreePatternId {
    std::string value;
};

enum class SpanningTreeConstraintDisposition {
    absorbed_by_tree_pattern,
    closure_residual,
    unsupported,
};

struct SpanningTreePatternMatch {
    SpanningTreePatternId pattern_id;
    kernel::RigidSetId parent_rigid_set_id;
    kernel::RigidSetId child_rigid_set_id;
    std::vector<kernel::ConstraintId> absorbed_constraint_ids;
    std::vector<kernel::ConstraintId> closure_constraint_ids;
    std::vector<kernel::ConstraintId> unsupported_constraint_ids;
    int removed_rotational_dof = 0;
    int removed_translational_dof = 0;
    int weight = 0;
    bool supported = false;
    std::string unsupported_code;
};

struct RigidSetTreeEdge {
    int edge_id = 0;
    kernel::RigidSetId parent_rigid_set_id;
    kernel::RigidSetId child_rigid_set_id;
    SpanningTreePatternMatch pattern_match;
};

struct RigidSetSpanningForestPlan {
    std::vector<kernel::RigidSetId> rigid_set_ids;
    std::vector<RigidSetTreeEdge> selected_edges;
    std::vector<kernel::ConstraintId> absorbed_constraint_ids;
    std::vector<kernel::ConstraintId> closure_constraint_ids;
    std::vector<kernel::ConstraintId> unsupported_constraint_ids;
    kernel::StageReport report;
};

struct SpanningForestValidationReport {
    bool valid = true;
    bool every_active_constraint_partitioned_once = true;
    bool tree_edges_acyclic = true;
    bool selected_edges_have_supported_pattern = true;
    bool unsupported_constraints_have_report_code = true;
    bool no_same_rigid_set_tree_edges = true;
    int absorbed_count = 0;
    int closure_count = 0;
    int unsupported_count = 0;
    int total_active_constraints = 0;
    std::vector<kernel::ReportMessage> messages;
};

struct PlannerOutput {
    CoverPlan cover_plan;
    std::vector<ContextSnapshot> overlap_contexts;
    std::vector<BoundaryProjection> boundary_projections;
    std::vector<Subproblem> subproblems;
    std::vector<SolveStep> solve_order;
    SolveDag solve_dag;
    GaugePolicy gauge_policy;
    RigidSetSpanningForestPlan spanning_forest_plan;
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

struct SolveDagValidationReport {
    bool valid = true;
    bool nodes_reference_known_contexts = true;
    bool edges_reference_known_nodes = true;
    bool edge_projections_reference_known_cover_projections = true;
    bool acyclic = true;
    bool covers_all_subproblems = true;
    int node_count = 0;
    int edge_count = 0;
    std::vector<ReportMessage> messages;
};

PlannerOutput plan_decomposition(const PlannerInput& input);
gcs::kernel::ContractResult<RigidSetSpanningForestPlan> plan_spanning_forest(
    const ModelSnapshot& model,
    const graph::IncidenceIndices& incidence,
    const SolveIntent& solve_intent);
gcs::kernel::ContractResult<SpanningForestValidationReport> validate_spanning_forest(
    const ModelSnapshot& model,
    const RigidSetSpanningForestPlan& forest_plan);
gcs::kernel::ContractResult<CoverValidationReport> validate_cover(
    const ModelSnapshot& model,
    const CoverPlan& cover_plan);
gcs::kernel::ContractResult<SolveOrderValidationReport> validate_solve_order(
    const PlannerOutput& output);
gcs::kernel::ContractResult<SolveDagValidationReport> validate_solve_dag(
    const PlannerOutput& output);

}
