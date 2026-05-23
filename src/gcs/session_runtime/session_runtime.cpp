module;

#include <string>
#include <utility>
#include <vector>

module gcs.session_runtime;

import gcs.kernel;
import gcs.constraint_catalog;
import gcs.incidence_graph;
import gcs.decomposition_planner;
import gcs.numeric_engine;
import gcs.diagnostics;

namespace gcs::runtime {

namespace kernel = gcs::kernel;

SessionRuntime::SessionRuntime(ModelSnapshot snapshot)
    : current_snapshot_(std::move(snapshot)) {}

void SessionRuntime::load_snapshot(ModelSnapshot snapshot) {
    current_snapshot_ = std::move(snapshot);
}

const ModelSnapshot& SessionRuntime::current_snapshot() const {
    return current_snapshot_;
}

CommandResult SessionRuntime::solve(SolveIntent intent) {
    return execute(make_solve_command(std::move(intent)));
}

CommandResult SessionRuntime::execute(const Command& command) {
    CommandResult result;
    if (command.kind != CommandKind::solve) {
        result.user_visible_status = SolveStatus::unsupported;
        result.obstruction_report = diagnostics::make_obstruction(
            "runtime.unsupported_command",
            "Only solve commands are supported by the first runtime skeleton.");
        return result;
    }

    current_snapshot_.solve_intent = command.solve_intent;

    StageReport validation_report = constraints::validate_model_constraints(current_snapshot_);
    result.stage_reports.push_back(validation_report);
    if (validation_report.status == kernel::StageStatus::error) {
        result.user_visible_status = SolveStatus::invalid_model;
        result.obstruction_report = diagnostics::make_obstruction(
            "runtime.invalid_model",
            "Constraint catalog validation failed before planning.");
        return result;
    }

    graph::IncidenceIndices incidence =
        graph::build_incidence_indices(graph::IncidenceInput{current_snapshot_});
    result.stage_reports.push_back(incidence.report);
    if (incidence.report.status == kernel::StageStatus::error) {
        result.user_visible_status = SolveStatus::invalid_model;
        result.obstruction_report = diagnostics::make_obstruction(
            "runtime.invalid_incidence",
            "Incidence graph construction failed.");
        return result;
    }

    result.planner_output = planning::plan_decomposition(
        planning::PlannerInput{current_snapshot_, incidence, command.solve_intent, {}});
    result.stage_reports.push_back(result.planner_output.structural_report);

    kernel::ContextSnapshot root_context = kernel::make_whole_model_context(current_snapshot_);
    diagnostics::DiagnosticInput pre_solve_input;
    pre_solve_input.phase = diagnostics::DiagnosticPhase::pre_solve;
    pre_solve_input.model = current_snapshot_;
    pre_solve_input.context = root_context;
    pre_solve_input.gauge_policy = result.planner_output.gauge_policy;
    result.pre_solve_diagnostics = diagnostics::diagnose(pre_solve_input);

    std::vector<kernel::LocalSection> local_sections;
    for (const auto& subproblem : result.planner_output.subproblems) {
        const kernel::ContextSnapshot* context = nullptr;
        for (const auto& candidate : result.planner_output.cover_plan.contexts) {
            if (candidate.id == subproblem.context_id) {
                context = &candidate;
                break;
            }
        }
        if (context == nullptr) {
            result.user_visible_status = SolveStatus::invalid_model;
            result.obstruction_report = diagnostics::make_obstruction(
                "runtime.missing_context",
                "Planner produced a subproblem whose context is absent from the cover plan.");
            return result;
        }

        auto task = numeric::make_numeric_task(
            current_snapshot_,
            *context,
            subproblem.active_variables,
            subproblem.active_equations,
            result.planner_output.gauge_policy);
        task.boundary_variables = subproblem.boundary_variables;

        auto numeric_report = numeric::solve_local(task);
        local_sections.push_back(numeric_report.local_section);
        result.stage_reports.push_back(numeric_report.stage_report);
        result.numeric_reports.push_back(numeric_report);

        if (numeric_report.result_code != SolveStatus::solved) {
            result.user_visible_status = numeric_report.result_code;
            result.obstruction_report = diagnostics::make_obstruction(
                "runtime.numeric_failure",
                numeric_report.failure_cause.empty()
                    ? "Numeric engine failed."
                    : numeric_report.failure_cause);
            return result;
        }
    }

    result.gluing_report = diagnostics::glue_local_sections(
        diagnostics::GluingInput{
            current_snapshot_,
            result.planner_output.cover_plan,
            local_sections,
            result.planner_output.boundary_projections,
            result.planner_output.gauge_policy,
            current_snapshot_.tolerances});
    result.stage_reports.push_back(result.gluing_report.stage_report);

    if (!result.gluing_report.accepted) {
        result.user_visible_status = SolveStatus::inconsistent;
        result.obstruction_report = result.gluing_report.obstruction_report;
        return result;
    }

    commit_accepted_state(result.gluing_report.proposed_global_state);
    result.accepted = true;
    result.new_state_version = current_snapshot_.state_version;
    result.user_visible_status =
        result.pre_solve_diagnostics.status_code == SolveStatus::solved
            ? SolveStatus::solved
            : SolveStatus::accepted_with_warnings;
    return result;
}

Command SessionRuntime::make_solve_command(SolveIntent intent) {
    Command command;
    command.id = next_command_id_;
    next_command_id_ = CommandId{next_command_id_.value + 1};
    command.kind = CommandKind::solve;
    command.solve_intent = std::move(intent);
    command.model_edit_or_solve_request = current_snapshot_;
    return command;
}

void SessionRuntime::commit_accepted_state(const ProposedState& proposed_state) {
    for (const auto& state : proposed_state.entity_states) {
        for (auto& entity : current_snapshot_.entities) {
            if (entity.id == state.entity_id) {
                entity.parameters = state.parameters;
                break;
            }
        }
    }
    current_snapshot_.state_version = kernel::next_version(current_snapshot_.state_version);
}

}
