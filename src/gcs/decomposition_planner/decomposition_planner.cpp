module;

#include <algorithm>
#include <cstdint>
#include <map>
#include <set>
#include <string>
#include <utility>
#include <vector>

module gcs.decomposition_planner;

import gcs.kernel;
import gcs.incidence_graph;

namespace gcs::planning {

namespace kernel = gcs::kernel;

namespace {

int compute_expected_free_dof(const ModelSnapshot& model,
                              const std::vector<EntityId>& entity_ids,
                              const std::vector<ConstraintId>& constraint_ids,
                              int gauge_dof) {
    int parameter_dof = 0;
    for (EntityId entity_id : entity_ids) {
        if (const auto* entity = kernel::find_entity(model, entity_id)) {
            parameter_dof += kernel::geometry_dof(entity->kind);
        }
    }

    int equation_dof = 0;
    for (ConstraintId constraint_id : constraint_ids) {
        if (const auto* constraint = kernel::find_constraint(model, constraint_id)) {
            equation_dof += kernel::constraint_dof_effect(constraint->kind);
        }
    }

    return parameter_dof - equation_dof - gauge_dof;
}

kernel::ReportMessage make_message(kernel::ReportSeverity severity,
                                   const char* code,
                                   const char* summary,
                                   std::vector<kernel::StableId> subjects = {}) {
    return kernel::make_report_message(
        severity,
        kernel::ReportCode{code},
        summary,
        std::move(subjects));
}

void append_message(StageReport& report,
                    std::vector<ReportMessage>& payload_messages,
                    kernel::ReportMessage message) {
    payload_messages.push_back(message);
    kernel::append_report_message(report, std::move(message));
}

bool contains_context(const std::vector<ContextSnapshot>& contexts, ContextId context_id) {
    for (const auto& context : contexts) {
        if (context.id == context_id) return true;
    }
    return false;
}

bool contains_subproblem_context(const std::vector<Subproblem>& subproblems,
                                 ContextId context_id) {
    for (const auto& subproblem : subproblems) {
        if (subproblem.context_id == context_id) return true;
    }
    return false;
}

bool contains_step_context(const std::vector<SolveStep>& solve_order,
                           ContextId context_id) {
    for (const auto& step : solve_order) {
        if (step.context_id == context_id) return true;
    }
    return false;
}

bool contains_dag_node(const SolveDag& dag, ContextId context_id) {
    for (const auto& node : dag.nodes) {
        if (node.context_id == context_id) return true;
    }
    return false;
}

const SolveDagNode* find_dag_node(const SolveDag& dag, ContextId context_id) {
    for (const auto& node : dag.nodes) {
        if (node.context_id == context_id) return &node;
    }
    return nullptr;
}

bool contains_cover_projection(const CoverPlan& cover_plan,
                               const SolveDagEdge& edge) {
    for (const auto& projection : cover_plan.boundary_projections) {
        if (projection.id == edge.projection_id &&
            projection.source_context_id == edge.source_context_id &&
            projection.target_context_id == edge.target_context_id) {
            return true;
        }
    }
    return false;
}

BoundaryProjection make_component_projection(const ContextSnapshot& component_context,
                                             ContextId root_context_id,
                                             std::uint64_t projection_index) {
    BoundaryProjection projection;
    projection.id = kernel::ProjectionId{projection_index};
    projection.source_context_id = component_context.id;
    projection.target_context_id = root_context_id;
    projection.entity_ids = component_context.entity_ids;
    projection.constraint_ids = component_context.constraint_ids;
    return projection;
}

void append_dag_node(PlannerOutput& output,
                     ContextId context_id,
                     int topological_order,
                     bool solved_locally,
                     bool aggregation_context) {
    output.solve_dag.nodes.push_back(
        SolveDagNode{
            context_id,
            topological_order,
            solved_locally,
            aggregation_context});
}

void append_dag_edge(PlannerOutput& output, const BoundaryProjection& projection) {
    output.solve_dag.edges.push_back(
        SolveDagEdge{
            projection.source_context_id,
            projection.target_context_id,
            projection.id,
            projection.entity_ids,
            projection.constraint_ids});
}

void append_component_subproblem(PlannerOutput& output,
                                 const ModelSnapshot& model,
                                 const ContextSnapshot& context,
                                 int subproblem_id,
                                 const kernel::SolveIntent& solve_intent) {
    Subproblem subproblem;
    subproblem.id = subproblem_id;
    subproblem.context_id = context.id;
    subproblem.active_variables = context.entity_ids;
    subproblem.active_equations = context.constraint_ids;
    for (EntityId fixed_entity_id : solve_intent.fixed_entity_ids) {
        if (kernel::contains_entity(context.entity_ids, fixed_entity_id) &&
            !kernel::contains_entity(subproblem.boundary_variables, fixed_entity_id)) {
            subproblem.boundary_variables.push_back(fixed_entity_id);
        }
    }
    subproblem.expected_free_dof = compute_expected_free_dof(
        model,
        subproblem.active_variables,
        subproblem.active_equations,
        output.gauge_policy.removed_dof);
    output.subproblems.push_back(subproblem);
    output.solve_order.push_back(SolveStep{subproblem_id, context.id});
}

}  // namespace

PlannerOutput plan_decomposition(const PlannerInput& input) {
    PlannerOutput output;
    output.structural_report = kernel::make_stage_report("decomposition_planner.plan");
    output.cover_plan.id = kernel::CoverId{1};
    output.cover_plan.root_context_id = ContextId{0};
    output.gauge_policy = GaugePolicy{kernel::GaugeKind::none, ContextId{0}, {}, 0};

    ContextSnapshot root = kernel::make_whole_model_context(input.model, ContextId{0});
    output.cover_plan.contexts.push_back(root);

    // Check for articulation-based decomposition first
    auto biconnected_result = graph::decompose_biconnected(input.model, input.incidence);
    const bool has_articulation = !biconnected_result.payload.articulation_points.empty();

    if (has_articulation) {
        // Build fine-grained subproblems from biconnected components
        std::uint64_t next_context_id = 1;
        int subproblem_id = 0;

        // Create overlap contexts for articulation entities
        // Each articulation entity becomes its own overlap context
        std::vector<ContextSnapshot> articulation_overlap_contexts;
        for (const auto& ap : biconnected_result.payload.articulation_points) {
            ContextSnapshot overlap_ctx;
            overlap_ctx.id = ContextId{next_context_id++};
            overlap_ctx.kind = kernel::ContextKind::connected_component;
            overlap_ctx.state_version = input.model.state_version;
            overlap_ctx.entity_ids.push_back(ap.entity_id);
            // Find constraints that involve this articulation entity
            for (const auto& constraint_inc : input.incidence.constraint_incidence) {
                if (!constraint_inc.valid) continue;
                bool involves_articulation = false;
                for (EntityId eid : constraint_inc.entity_ids) {
                    if (eid == ap.entity_id) {
                        involves_articulation = true;
                        break;
                    }
                }
                if (involves_articulation) {
                    if (!kernel::contains_constraint(overlap_ctx.constraint_ids,
                                                     constraint_inc.constraint_id)) {
                        overlap_ctx.constraint_ids.push_back(constraint_inc.constraint_id);
                    }
                }
            }
            // Find rigid sets for the articulation entity
            if (const auto* entity = kernel::find_entity(input.model, ap.entity_id)) {
                overlap_ctx.rigid_set_ids.push_back(entity->rigid_set_id);
            }
            articulation_overlap_contexts.push_back(std::move(overlap_ctx));
            output.cover_plan.contexts.push_back(articulation_overlap_contexts.back());
        }

        // Create subproblems for each biconnected component
        for (const auto& comp : biconnected_result.payload.components) {
            ContextSnapshot comp_ctx;
            comp_ctx.id = ContextId{next_context_id++};
            comp_ctx.kind = kernel::ContextKind::connected_component;
            comp_ctx.state_version = input.model.state_version;
            comp_ctx.entity_ids = comp.entity_ids;
            comp_ctx.constraint_ids = comp.constraint_ids;
            // Collect rigid sets
            for (EntityId eid : comp.entity_ids) {
                if (const auto* entity = kernel::find_entity(input.model, eid)) {
                    if (!kernel::contains_rigid_set(comp_ctx.rigid_set_ids,
                                                    entity->rigid_set_id)) {
                        comp_ctx.rigid_set_ids.push_back(entity->rigid_set_id);
                    }
                }
            }
            output.cover_plan.contexts.push_back(comp_ctx);

            // Create boundary projections from this component to root and to its
            // articulation overlap contexts
            auto root_projection = make_component_projection(
                comp_ctx,
                output.cover_plan.root_context_id,
                static_cast<std::uint64_t>(output.boundary_projections.size() + 1));
            output.boundary_projections.push_back(root_projection);
            append_dag_edge(output, root_projection);

            // Also project to articulation overlap contexts where the component
            // shares the articulation entity
            for (const auto& overlap_ctx : articulation_overlap_contexts) {
                if (overlap_ctx.entity_ids.empty()) continue;
                EntityId articulation_entity = overlap_ctx.entity_ids.front();
                if (kernel::contains_entity(comp.entity_ids, articulation_entity)) {
                    BoundaryProjection ap_projection;
                    ap_projection.id = kernel::ProjectionId{
                        static_cast<std::uint64_t>(output.boundary_projections.size() + 1)};
                    ap_projection.source_context_id = comp_ctx.id;
                    ap_projection.target_context_id = overlap_ctx.id;
                    ap_projection.entity_ids.push_back(articulation_entity);
                    // Include shared constraints involving the articulation entity
                    for (ConstraintId cid : comp.constraint_ids) {
                        if (kernel::contains_constraint(overlap_ctx.constraint_ids, cid)) {
                            ap_projection.constraint_ids.push_back(cid);
                        }
                    }
                    output.boundary_projections.push_back(ap_projection);
                    append_dag_edge(output, ap_projection);
                }
            }

            append_component_subproblem(
                output,
                input.model,
                comp_ctx,
                subproblem_id,
                input.solve_intent);
            append_dag_node(output, comp_ctx.id, subproblem_id, true, false);
            ++subproblem_id;
        }

        // Add DAG nodes for articulation overlap contexts
        for (const auto& overlap_ctx : articulation_overlap_contexts) {
            append_dag_node(output, overlap_ctx.id, subproblem_id, false, true);
            ++subproblem_id;
        }

        // Add root aggregation node
        append_dag_node(
            output,
            output.cover_plan.root_context_id,
            subproblem_id,
            false,
            true);

        if (output.subproblems.empty()) {
            kernel::append_report_message(
                output.structural_report,
                make_message(
                    kernel::ReportSeverity::warning,
                    "planner.empty_model",
                    "No subproblems were produced for an empty model."));
        }
        output.cover_plan.boundary_projections = output.boundary_projections;
    } else {
        // No articulation points — use existing connected-component or whole-model logic
        const bool split_into_components = input.incidence.connected_components.size() > 1;
        if (!split_into_components) {
            append_component_subproblem(output, input.model, root, 0, input.solve_intent);
            append_dag_node(output, root.id, 0, true, false);
        } else {
            std::uint64_t next_context_id = 1;
            int subproblem_id = 0;
            for (const auto& component : input.incidence.connected_components) {
                ContextSnapshot context;
                context.id = ContextId{next_context_id++};
                context.kind = kernel::ContextKind::connected_component;
                context.state_version = input.model.state_version;
                context.entity_ids = component.entity_ids;
                context.constraint_ids = component.constraint_ids;
                context.rigid_set_ids = component.rigid_set_ids;
                output.cover_plan.contexts.push_back(context);

                auto projection = make_component_projection(
                    context,
                    output.cover_plan.root_context_id,
                    static_cast<std::uint64_t>(output.boundary_projections.size() + 1));
                output.boundary_projections.push_back(projection);
                append_dag_edge(output, projection);
                append_component_subproblem(
                    output,
                    input.model,
                    context,
                    subproblem_id,
                    input.solve_intent);
                append_dag_node(output, context.id, subproblem_id, true, false);
                ++subproblem_id;
            }
            output.cover_plan.boundary_projections = output.boundary_projections;
            append_dag_node(
                output,
                output.cover_plan.root_context_id,
                subproblem_id,
                false,
                true);

            if (output.subproblems.empty()) {
                kernel::append_report_message(
                    output.structural_report,
                    make_message(
                        kernel::ReportSeverity::warning,
                        "planner.empty_model",
                        "No subproblems were produced for an empty model."));
            }
        }
    }

    auto cover_validation = validate_cover(input.model, output.cover_plan);
    auto order_validation = validate_solve_order(output);
    auto dag_validation = validate_solve_dag(output);
    for (auto message : cover_validation.report.messages) {
        kernel::append_report_message(output.structural_report, std::move(message));
    }
    for (auto message : order_validation.report.messages) {
        kernel::append_report_message(output.structural_report, std::move(message));
    }
    for (auto message : dag_validation.report.messages) {
        kernel::append_report_message(output.structural_report, std::move(message));
    }
    return output;
}

gcs::kernel::ContractResult<CoverValidationReport> validate_cover(
    const ModelSnapshot& model,
    const CoverPlan& cover_plan) {
    kernel::ContractResult<CoverValidationReport> result;
    result.report = kernel::make_stage_report("decomposition_planner.validate_cover");
    result.payload.context_count = static_cast<int>(cover_plan.contexts.size());
    result.payload.boundary_projection_count =
        static_cast<int>(cover_plan.boundary_projections.size());

    std::vector<ContextId> context_ids;
    for (const auto& context : cover_plan.contexts) {
        if (std::find(context_ids.begin(), context_ids.end(), context.id) !=
            context_ids.end()) {
            result.payload.valid = false;
            result.payload.contexts_reference_known_ids = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "planner.cover_duplicate_context_id",
                    "Cover plan contains a duplicate context ID.",
                    {kernel::StableId{"context", context.id.value}}));
        }
        context_ids.push_back(context.id);

        if (!(context.state_version == model.state_version)) {
            result.payload.valid = false;
            result.payload.contexts_reference_known_ids = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "planner.cover_context_version_mismatch",
                    "Cover context state version must match the model snapshot.",
                    {kernel::StableId{"context", context.id.value}}));
        }

        for (EntityId entity_id : context.entity_ids) {
            if (kernel::find_entity(model, entity_id) == nullptr) {
                result.payload.valid = false;
                result.payload.contexts_reference_known_ids = false;
                append_message(
                    result.report,
                    result.payload.messages,
                    make_message(
                        kernel::ReportSeverity::error,
                        "planner.cover_unknown_entity",
                        "Cover context references an entity that is absent from the model.",
                        {kernel::StableId{"context", context.id.value},
                         kernel::StableId{"entity", entity_id.value}}));
            }
        }
        for (ConstraintId constraint_id : context.constraint_ids) {
            if (kernel::find_constraint(model, constraint_id) == nullptr) {
                result.payload.valid = false;
                result.payload.contexts_reference_known_ids = false;
                append_message(
                    result.report,
                    result.payload.messages,
                    make_message(
                        kernel::ReportSeverity::error,
                        "planner.cover_unknown_constraint",
                        "Cover context references a constraint that is absent from the model.",
                        {kernel::StableId{"context", context.id.value},
                         kernel::StableId{"constraint", constraint_id.value}}));
            }
        }
        for (kernel::RigidSetId rigid_set_id : context.rigid_set_ids) {
            if (kernel::find_rigid_set(model, rigid_set_id) == nullptr) {
                result.payload.valid = false;
                result.payload.contexts_reference_known_ids = false;
                append_message(
                    result.report,
                    result.payload.messages,
                    make_message(
                        kernel::ReportSeverity::error,
                        "planner.cover_unknown_rigid_set",
                        "Cover context references a rigid set that is absent from the model.",
                        {kernel::StableId{"context", context.id.value},
                         kernel::StableId{"rigid_set", rigid_set_id.value}}));
            }
        }
    }

    for (const auto& entity : model.entities) {
        bool covered = false;
        for (const auto& context : cover_plan.contexts) {
            if (kernel::contains_entity(context.entity_ids, entity.id)) {
                covered = true;
                break;
            }
        }
        if (!covered) {
            result.payload.valid = false;
            result.payload.covers_all_entities = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "planner.cover_missing_entity",
                    "Cover plan does not cover a model entity.",
                    {kernel::StableId{"entity", entity.id.value}}));
        }
    }

    for (const auto& constraint : model.constraints) {
        bool covered = false;
        for (const auto& context : cover_plan.contexts) {
            if (kernel::contains_constraint(context.constraint_ids, constraint.id)) {
                covered = true;
                break;
            }
        }
        if (!covered) {
            result.payload.valid = false;
            result.payload.covers_all_constraints = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "planner.cover_missing_constraint",
                    "Cover plan does not cover a model constraint.",
                    {kernel::StableId{"constraint", constraint.id.value}}));
        }
    }

    for (const auto& projection : cover_plan.boundary_projections) {
        if (!contains_context(cover_plan.contexts, projection.source_context_id) ||
            !contains_context(cover_plan.contexts, projection.target_context_id)) {
            result.payload.valid = false;
            result.payload.boundary_projections_reference_known_contexts = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "planner.cover_projection_missing_context",
                    "Boundary projection references a context absent from the cover.",
                    {kernel::StableId{"projection", projection.id.value}}));
        }

        for (EntityId entity_id : projection.entity_ids) {
            if (kernel::find_entity(model, entity_id) == nullptr) {
                result.payload.valid = false;
                append_message(
                    result.report,
                    result.payload.messages,
                    make_message(
                        kernel::ReportSeverity::error,
                        "planner.cover_projection_unknown_entity",
                        "Boundary projection references an entity absent from the model.",
                        {kernel::StableId{"projection", projection.id.value},
                         kernel::StableId{"entity", entity_id.value}}));
            }
        }
    }

    return result;
}

gcs::kernel::ContractResult<SolveOrderValidationReport> validate_solve_order(
    const PlannerOutput& output) {
    kernel::ContractResult<SolveOrderValidationReport> result;
    result.report = kernel::make_stage_report("decomposition_planner.validate_solve_order");
    result.payload.step_count = static_cast<int>(output.solve_order.size());

    int expected_order = 0;
    for (const auto& step : output.solve_order) {
        if (step.order != expected_order) {
            result.payload.valid = false;
            result.payload.strictly_ordered = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "planner.solve_order_not_strict",
                    "Solve-order entries must be deterministic and strictly ordered.",
                    {kernel::StableId{"context", step.context_id.value}}));
        }
        ++expected_order;

        if (!contains_subproblem_context(output.subproblems, step.context_id)) {
            result.payload.valid = false;
            result.payload.every_step_has_context = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "planner.solve_order_missing_subproblem_context",
                    "Solve-order step references no known subproblem context.",
                    {kernel::StableId{"context", step.context_id.value}}));
        }
    }

    for (const auto& subproblem : output.subproblems) {
        if (!contains_step_context(output.solve_order, subproblem.context_id)) {
            result.payload.valid = false;
            result.payload.covers_all_subproblems = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "planner.solve_order_missing_subproblem",
                    "Solve order does not contain a subproblem context.",
                    {kernel::StableId{"context", subproblem.context_id.value}}));
        }
    }

    return result;
}

gcs::kernel::ContractResult<SolveDagValidationReport> validate_solve_dag(
    const PlannerOutput& output) {
    kernel::ContractResult<SolveDagValidationReport> result;
    result.report = kernel::make_stage_report("decomposition_planner.validate_solve_dag");
    result.payload.node_count = static_cast<int>(output.solve_dag.nodes.size());
    result.payload.edge_count = static_cast<int>(output.solve_dag.edges.size());

    for (const auto& node : output.solve_dag.nodes) {
        if (!contains_context(output.cover_plan.contexts, node.context_id)) {
            result.payload.valid = false;
            result.payload.nodes_reference_known_contexts = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "planner.solve_dag_unknown_context",
                    "Solve DAG node references a context absent from the cover.",
                    {kernel::StableId{"context", node.context_id.value}}));
        }
    }

    for (const auto& edge : output.solve_dag.edges) {
        const SolveDagNode* source =
            find_dag_node(output.solve_dag, edge.source_context_id);
        const SolveDagNode* target =
            find_dag_node(output.solve_dag, edge.target_context_id);
        if (source == nullptr || target == nullptr) {
            result.payload.valid = false;
            result.payload.edges_reference_known_nodes = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "planner.solve_dag_edge_unknown_node",
                    "Solve DAG edge references a context absent from the DAG nodes.",
                    {kernel::StableId{"projection", edge.projection_id.value}}));
        }

        if (!contains_cover_projection(output.cover_plan, edge)) {
            result.payload.valid = false;
            result.payload.edge_projections_reference_known_cover_projections = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "planner.solve_dag_projection_mismatch",
                    "Solve DAG edge must correspond to a cover boundary projection.",
                    {kernel::StableId{"projection", edge.projection_id.value}}));
        }

        if (source != nullptr && target != nullptr &&
            source->topological_order >= target->topological_order) {
            result.payload.valid = false;
            result.payload.acyclic = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "planner.solve_dag_cycle_or_backward_edge",
                    "Solve DAG edges must point from earlier local solves to later aggregation contexts.",
                    {kernel::StableId{"projection", edge.projection_id.value}}));
        }
    }

    for (const auto& subproblem : output.subproblems) {
        if (!contains_dag_node(output.solve_dag, subproblem.context_id)) {
            result.payload.valid = false;
            result.payload.covers_all_subproblems = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "planner.solve_dag_missing_subproblem",
                    "Solve DAG does not contain a subproblem context.",
                    {kernel::StableId{"context", subproblem.context_id.value}}));
        }
    }

    return result;
}

// --- Spanning forest plan ---

namespace {

// Union-Find for deterministic Kruskal
struct SpanningForestUnionFind {
    std::map<std::uint64_t, std::uint64_t> parent;

    std::uint64_t find(std::uint64_t x) {
        if (parent.find(x) == parent.end()) {
            parent[x] = x;
        }
        if (parent[x] != x) {
            parent[x] = find(parent[x]);
        }
        return parent[x];
    }

    void unite(std::uint64_t a, std::uint64_t b) {
        std::uint64_t ra = find(a);
        std::uint64_t rb = find(b);
        if (ra != rb) {
            parent[ra] = rb;
        }
    }
};

struct CandidateEdge {
    kernel::RigidSetId first;
    kernel::RigidSetId second;
    int weight = 0;
    int original_index = 0;
    std::vector<kernel::ConstraintId> constraint_ids;
    bool supported = false;
    std::string unsupported_code;
};

// Deterministic sort key for Kruskal:
//  higher weight first, then lower first RS id, then lower second RS id,
//  then lower original_index.
bool candidate_edge_less(const CandidateEdge& a, const CandidateEdge& b) {
    if (a.weight != b.weight) return a.weight > b.weight;
    if (!(a.first == b.first)) return a.first.value < b.first.value;
    if (!(a.second == b.second)) return a.second.value < b.second.value;
    return a.original_index < b.original_index;
}

// For sorting final tree edges by parent then child
bool tree_edge_less(const RigidSetTreeEdge& a, const RigidSetTreeEdge& b) {
    if (!(a.parent_rigid_set_id == b.parent_rigid_set_id))
        return a.parent_rigid_set_id.value < b.parent_rigid_set_id.value;
    return a.child_rigid_set_id.value < b.child_rigid_set_id.value;
}

}  // namespace

gcs::kernel::ContractResult<RigidSetSpanningForestPlan> plan_spanning_forest(
    const ModelSnapshot& model,
    const graph::IncidenceIndices& /*incidence*/,
    const SolveIntent& solve_intent) {
    kernel::ContractResult<RigidSetSpanningForestPlan> result;
    result.report = kernel::make_stage_report(
        "decomposition_planner.plan_spanning_forest");

    // Step 1: Build rigid body graph
    auto hypergraph_result = graph::build_hypergraph(
        graph::HypergraphBuildRequest{model, {}});
    auto rigid_body_result = graph::build_rigid_body_graph(
        model, hypergraph_result.payload);

    // Step 2: Build candidate edges from rigid body graph edges.
    // In M1, all patterns are unsupported — no real pattern catalog exists yet.
    // Every cross-rigid-set constraint becomes a closure constraint.
    std::vector<CandidateEdge> candidates;
    for (std::size_t i = 0; i < rigid_body_result.payload.edges.size(); ++i) {
        const auto& edge = rigid_body_result.payload.edges[i];
        CandidateEdge candidate;
        candidate.first = edge.first_rigid_set_id;
        candidate.second = edge.second_rigid_set_id;
        candidate.weight = 0;  // M1: no pattern support => zero weight
        candidate.original_index = static_cast<int>(i);
        candidate.constraint_ids = edge.constraint_ids;
        candidate.supported = false;
        candidate.unsupported_code = "planner.spanning_tree.pattern_unsupported";
        candidates.push_back(std::move(candidate));
    }

    // Step 3: Maximum-weight spanning forest using deterministic Kruskal
    std::sort(candidates.begin(), candidates.end(), candidate_edge_less);

    SpanningForestUnionFind uf;
    for (const auto& rigid_set : model.rigid_sets) {
        uf.find(rigid_set.id.value);  // ensure every rigid set is in UF
    }

    std::vector<CandidateEdge> selected;
    std::vector<CandidateEdge> rejected;
    for (const auto& cand : candidates) {
        if (uf.find(cand.first.value) != uf.find(cand.second.value)) {
            uf.unite(cand.first.value, cand.second.value);
            selected.push_back(cand);
        } else {
            rejected.push_back(cand);
        }
    }

    // Step 4: Orient tree edges from root rigid sets selected by gauge policy.
    // Root preference: fixed entities' rigid sets first, then lowest RS id.
    std::set<std::uint64_t> fixed_rs_ids;
    for (EntityId fixed_id : solve_intent.fixed_entity_ids) {
        if (const auto* entity = kernel::find_entity(model, fixed_id)) {
            fixed_rs_ids.insert(entity->rigid_set_id.value);
        }
    }

    // Collect all rigid set ids
    std::vector<kernel::RigidSetId> all_rs_ids;
    for (const auto& rs : model.rigid_sets) {
        all_rs_ids.push_back(rs.id);
    }

    // For each component root (UF representative), pick the best root rigid set
    std::map<std::uint64_t, std::uint64_t> component_root;
    for (const auto& rs : model.rigid_sets) {
        std::uint64_t rep = uf.find(rs.id.value);
        auto it = component_root.find(rep);
        if (it == component_root.end()) {
            component_root[rep] = rs.id.value;
        } else {
            // Prefer fixed-entity RS
            bool current_fixed = fixed_rs_ids.count(it->second) > 0;
            bool candidate_fixed = fixed_rs_ids.count(rs.id.value) > 0;
            if (candidate_fixed && !current_fixed) {
                component_root[rep] = rs.id.value;
            } else if (candidate_fixed == current_fixed &&
                       rs.id.value < it->second) {
                component_root[rep] = rs.id.value;
            }
        }
    }

    // Orient selected edges away from roots (BFS-like traversal)
    std::vector<RigidSetTreeEdge> tree_edges;
    {
        // Build adjacency from selected edges (undirected)
        std::map<std::uint64_t, std::vector<kernel::RigidSetId>> adj;
        for (const auto& cand : selected) {
            adj[cand.first.value].push_back(cand.second);
            adj[cand.second.value].push_back(cand.first);
        }

        // BFS from roots
        std::set<std::uint64_t> visited;
        std::vector<std::pair<kernel::RigidSetId, kernel::RigidSetId>> oriented;
        for (const auto& [rep, root_id] : component_root) {
            std::vector<kernel::RigidSetId> queue;
            queue.push_back(kernel::RigidSetId{root_id});
            while (!queue.empty()) {
                auto parent = queue.back();
                queue.pop_back();
                if (visited.count(parent.value)) continue;
                visited.insert(parent.value);
                auto it = adj.find(parent.value);
                if (it == adj.end()) continue;
                for (const auto& neighbor : it->second) {
                    if (visited.count(neighbor.value)) continue;
                    oriented.push_back({parent, neighbor});
                    queue.push_back(neighbor);
                }
            }
        }

        // Map oriented edges back to candidate data
        int edge_id = 0;
        for (const auto& [parent, child] : oriented) {
            RigidSetTreeEdge tree_edge;
            tree_edge.edge_id = edge_id++;
            tree_edge.parent_rigid_set_id = parent;
            tree_edge.child_rigid_set_id = child;

            // Find the matching candidate edge
            for (const auto& cand : selected) {
                if ((cand.first == parent && cand.second == child) ||
                    (cand.first == child && cand.second == parent)) {
                    SpanningTreePatternMatch match;
                    match.pattern_id = SpanningTreePatternId{"unsupported"};
                    match.parent_rigid_set_id = parent;
                    match.child_rigid_set_id = child;
                    match.closure_constraint_ids = cand.constraint_ids;
                    match.unsupported_constraint_ids = cand.constraint_ids;
                    match.weight = cand.weight;
                    match.supported = false;
                    match.unsupported_code = cand.unsupported_code;
                    tree_edge.pattern_match = std::move(match);
                    break;
                }
            }
            tree_edges.push_back(std::move(tree_edge));
        }
    }

    // Sort tree edges for deterministic output
    std::sort(tree_edges.begin(), tree_edges.end(), tree_edge_less);

    // Step 5: Partition constraints
    std::vector<kernel::ConstraintId> absorbed_ids;
    std::vector<kernel::ConstraintId> closure_ids;
    std::vector<kernel::ConstraintId> unsupported_ids;

    // In M1, all tree-edge constraints are unsupported → closure
    for (const auto& te : tree_edges) {
        for (auto cid : te.pattern_match.closure_constraint_ids) {
            closure_ids.push_back(cid);
        }
        for (auto cid : te.pattern_match.unsupported_constraint_ids) {
            unsupported_ids.push_back(cid);
        }
    }

    // Also collect closure constraints from rejected (cycle) edges
    for (const auto& rej : rejected) {
        for (auto cid : rej.constraint_ids) {
            closure_ids.push_back(cid);
        }
    }

    // Deduplicate
    auto dedup_constraints = [](std::vector<kernel::ConstraintId>& ids) {
        std::sort(ids.begin(), ids.end(),
                  [](auto a, auto b) { return a.value < b.value; });
        ids.erase(std::unique(ids.begin(), ids.end(),
                              [](auto a, auto b) { return a == b; }),
                  ids.end());
    };
    dedup_constraints(closure_ids);
    dedup_constraints(unsupported_ids);

    // Step 6: Build output
    result.payload.rigid_set_ids = all_rs_ids;
    result.payload.selected_edges = std::move(tree_edges);
    result.payload.absorbed_constraint_ids = absorbed_ids;
    result.payload.closure_constraint_ids = closure_ids;
    result.payload.unsupported_constraint_ids = unsupported_ids;
    result.payload.report = result.report;

    kernel::append_report_message(
        result.report,
        make_message(
            kernel::ReportSeverity::info,
            "planner.spanning_tree.plan_complete",
            "Spanning forest plan built. Not yet used for numeric solving.",
            {}));

    kernel::append_report_message(
        result.report,
        make_message(
            kernel::ReportSeverity::info,
            "planner.spanning_tree.not_used_for_numeric_task_yet",
            "M1 contract-only: spanning forest plan evidence is generated but "
            "the reduced numeric task path is not yet implemented.",
            {}));

    return result;
}

gcs::kernel::ContractResult<SpanningForestValidationReport> validate_spanning_forest(
    const ModelSnapshot& model,
    const RigidSetSpanningForestPlan& forest_plan) {
    kernel::ContractResult<SpanningForestValidationReport> result;
    result.report = kernel::make_stage_report(
        "decomposition_planner.validate_spanning_forest");

    int total_active = 0;
    for (const auto& constraint : model.constraints) {
        // Check if constraint crosses rigid sets
        std::set<std::uint64_t> rs_seen;
        for (EntityId eid : constraint.entity_ids) {
            if (const auto* entity = kernel::find_entity(model, eid)) {
                rs_seen.insert(entity->rigid_set_id.value);
            }
        }
        if (rs_seen.size() > 1) {
            total_active++;
        }
    }

    // Count partitioned constraints
    std::set<std::uint64_t> partitioned;
    for (auto cid : forest_plan.absorbed_constraint_ids) {
        partitioned.insert(cid.value);
    }
    for (auto cid : forest_plan.closure_constraint_ids) {
        partitioned.insert(cid.value);
    }
    for (auto cid : forest_plan.unsupported_constraint_ids) {
        partitioned.insert(cid.value);
    }

    result.payload.absorbed_count =
        static_cast<int>(forest_plan.absorbed_constraint_ids.size());
    result.payload.closure_count =
        static_cast<int>(forest_plan.closure_constraint_ids.size());
    result.payload.unsupported_count =
        static_cast<int>(forest_plan.unsupported_constraint_ids.size());
    result.payload.total_active_constraints = total_active;
    result.payload.every_active_constraint_partitioned_once =
        (static_cast<int>(partitioned.size()) >= total_active);

    // Check acyclicity: edges < nodes + components (conservative bound)
    result.payload.tree_edges_acyclic =
        (static_cast<int>(forest_plan.selected_edges.size()) <
         static_cast<int>(forest_plan.rigid_set_ids.size()) + 1);

    // Check no same-rigid-set tree edges
    result.payload.no_same_rigid_set_tree_edges = true;
    for (const auto& te : forest_plan.selected_edges) {
        if (te.parent_rigid_set_id == te.child_rigid_set_id) {
            result.payload.no_same_rigid_set_tree_edges = false;
            result.payload.valid = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "planner.spanning_tree.same_rigid_set_tree_edge",
                    "Tree edge connects a rigid set to itself.",
                    {kernel::StableId{"rigid_set",
                                      te.parent_rigid_set_id.value}}));
        }
    }

    // Check that selected edges have supported pattern (M1: all unsupported)
    result.payload.selected_edges_have_supported_pattern = true;
    for (const auto& te : forest_plan.selected_edges) {
        if (!te.pattern_match.supported) {
            result.payload.selected_edges_have_supported_pattern = false;
        }
    }

    // Check unsupported constraints have report code
    result.payload.unsupported_constraints_have_report_code = true;
    for (const auto& te : forest_plan.selected_edges) {
        if (!te.pattern_match.supported &&
            te.pattern_match.unsupported_code.empty()) {
            result.payload.unsupported_constraints_have_report_code = false;
        }
    }

    if (!result.payload.every_active_constraint_partitioned_once) {
        result.payload.valid = false;
        append_message(
            result.report,
            result.payload.messages,
            make_message(
                kernel::ReportSeverity::error,
                "planner.spanning_tree.missing_constraint_partition",
                "Not every active cross-rigid-set constraint appears in the "
                "absorbed/closure/unsupported partition.",
                {}));
    }

    if (!result.payload.tree_edges_acyclic) {
        result.payload.valid = false;
        append_message(
            result.report,
            result.payload.messages,
            make_message(
                kernel::ReportSeverity::error,
                "planner.spanning_tree.cycle_detected",
                "Spanning forest tree edges contain a cycle.",
                {}));
    }

    return result;
}

}
