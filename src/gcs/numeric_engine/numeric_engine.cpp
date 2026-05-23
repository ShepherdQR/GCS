module;

#include <algorithm>
#include <string>
#include <vector>

module gcs.numeric_engine;

import gcs.kernel;
import gcs.constraint_catalog;

namespace gcs::numeric {

namespace kernel = gcs::kernel;

NumericTask make_numeric_task(const ModelSnapshot& model,
                              const ContextSnapshot& context,
                              const std::vector<EntityId>& active_variables,
                              const std::vector<ConstraintId>& active_equations,
                              const GaugePolicy& gauge_policy) {
    NumericTask task;
    task.problem_snapshot = model;
    task.context_snapshot = context;
    task.active_variables = active_variables;
    task.active_equations = active_equations;
    task.tolerances = model.tolerances;
    task.gauge_policy = gauge_policy;
    return task;
}

NumericReport solve_local(const NumericTask& task) {
    NumericReport report;
    report.stage_report = kernel::make_stage_report("numeric_engine.solve_local");
    report.local_section.context_id = task.context_snapshot.id;
    report.local_section.entity_states = kernel::capture_entity_states(
        task.problem_snapshot,
        task.active_variables);
    report.local_section.valid = true;
    report.proposed_state.base_version = task.problem_snapshot.state_version;
    report.proposed_state.entity_states = report.local_section.entity_states;

    int equation_dof = 0;
    for (ConstraintId constraint_id : task.active_equations) {
        const auto* constraint = kernel::find_constraint(task.problem_snapshot, constraint_id);
        if (constraint == nullptr) {
            report.result_code = SolveStatus::invalid_model;
            report.local_section.valid = false;
            report.failure_cause = "Numeric task references a missing constraint.";
            kernel::append_report_message(
                report.stage_report,
                kernel::make_report_message(
                    kernel::ReportSeverity::error,
                    kernel::ReportCode{"numeric.missing_constraint"},
                    report.failure_cause,
                    {kernel::StableId{"constraint", constraint_id.value}}));
            return report;
        }
        equation_dof += constraints::generic_dof_effect(constraint->kind);
    }

    int variable_dof = 0;
    for (EntityId entity_id : task.active_variables) {
        const auto* entity = kernel::find_entity(task.problem_snapshot, entity_id);
        if (entity == nullptr) {
            report.result_code = SolveStatus::invalid_model;
            report.local_section.valid = false;
            report.failure_cause = "Numeric task references a missing entity.";
            kernel::append_report_message(
                report.stage_report,
                kernel::make_report_message(
                    kernel::ReportSeverity::error,
                    kernel::ReportCode{"numeric.missing_entity"},
                    report.failure_cause,
                    {kernel::StableId{"entity", entity_id.value}}));
            return report;
        }
        variable_dof += kernel::geometry_dof(entity->kind);
    }

    report.rank_estimate = std::min(
        equation_dof,
        std::max(0, variable_dof - task.gauge_policy.removed_dof));
    report.initial_residual = 0.0;
    report.final_residual = 0.0;
    report.step_norm = 0.0;
    report.condition_estimate = 1.0;
    report.iteration_count = 0;
    report.result_code = SolveStatus::solved;

    kernel::append_report_message(
        report.stage_report,
        kernel::make_report_message(
            kernel::ReportSeverity::info,
            kernel::ReportCode{"numeric.local_section.placeholder"},
            "Baseline numeric engine produced an identity local section.",
            {kernel::StableId{"context", task.context_snapshot.id.value}}));

    return report;
}

}
