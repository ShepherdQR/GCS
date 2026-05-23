module;

#include <cstdint>
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
        Subproblem subproblem;
        subproblem.id = 0;
        subproblem.context_id = root.id;
        subproblem.active_variables = root.entity_ids;
        subproblem.active_equations = root.constraint_ids;
        subproblem.expected_free_dof = compute_expected_free_dof(
            input.model,
            subproblem.active_variables,
            subproblem.active_equations,
            output.gauge_policy.removed_dof);
        output.subproblems.push_back(subproblem);
        output.solve_order.push_back(SolveStep{0, root.id});
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

        Subproblem subproblem;
        subproblem.id = subproblem_id;
        subproblem.context_id = context.id;
        subproblem.active_variables = context.entity_ids;
        subproblem.active_equations = context.constraint_ids;
        subproblem.expected_free_dof = compute_expected_free_dof(
            input.model,
            subproblem.active_variables,
            subproblem.active_equations,
            output.gauge_policy.removed_dof);
        output.subproblems.push_back(subproblem);
        output.solve_order.push_back(SolveStep{subproblem_id, context.id});
        ++subproblem_id;
    }

    if (output.subproblems.empty()) {
        kernel::append_report_message(
            output.structural_report,
            kernel::make_report_message(
                kernel::ReportSeverity::warning,
                kernel::ReportCode{"planner.empty_model"},
                "No subproblems were produced for an empty model."));
    }

    return output;
}

}
