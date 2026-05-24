module;

#include <algorithm>
#include <cstdint>
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
                                 int subproblem_id) {
    Subproblem subproblem;
    subproblem.id = subproblem_id;
    subproblem.context_id = context.id;
    subproblem.active_variables = context.entity_ids;
    subproblem.active_equations = context.constraint_ids;
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

    const bool split_into_components = input.incidence.connected_components.size() > 1;
    if (!split_into_components) {
        append_component_subproblem(output, input.model, root, 0);
        append_dag_node(output, root.id, 0, true, false);
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
        append_component_subproblem(output, input.model, context, subproblem_id);
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

}
