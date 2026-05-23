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

namespace {

kernel::ReportMessage make_message(kernel::ReportSeverity severity,
                                   const char* code,
                                   const std::string& summary,
                                   std::vector<kernel::StableId> subjects = {}) {
    return kernel::make_report_message(
        severity,
        kernel::ReportCode{code},
        summary,
        std::move(subjects));
}

SolveStatus status_from_stage(const StageReport& report) {
    if (report.status == kernel::StageStatus::error) return SolveStatus::failed;
    if (report.status == kernel::StageStatus::unsupported) return SolveStatus::unsupported;
    if (report.status == kernel::StageStatus::warning) {
        return SolveStatus::accepted_with_warnings;
    }
    return SolveStatus::solved;
}

std::string first_report_code(const StageReport& report) {
    if (report.messages.empty()) return {};
    return report.messages.front().code.value;
}

StageTraceEntry make_trace_entry(int order,
                                 const std::string& stage,
                                 const StageReport& stage_report,
                                 StateVersionId before_version,
                                 StateVersionId after_version,
                                 bool durable_mutation) {
    StageTraceEntry entry;
    entry.order = order;
    entry.stage = stage;
    entry.stage_status = stage_report.status;
    entry.status = status_from_stage(stage_report);
    entry.before_version = before_version;
    entry.after_version = after_version;
    entry.durable_mutation = durable_mutation;
    entry.code = first_report_code(stage_report);
    return entry;
}

void record_stage(CommandResult& result,
                  const std::string& stage,
                  const StageReport& report,
                  StateVersionId before_version,
                  StateVersionId after_version,
                  bool durable_mutation = false) {
    result.transaction_trace.stages.push_back(
        make_trace_entry(
            static_cast<int>(result.transaction_trace.stages.size()),
            stage,
            report,
            before_version,
            after_version,
            durable_mutation));
    result.stage_reports.push_back(report);
}

void rollback(CommandResult& result,
              const std::string& reason,
              StateVersionId restored_version) {
    result.transaction_trace.rolled_back = true;
    result.transaction_trace.rollback_reason = reason;
    result.transaction_trace.final_version = restored_version;
    result.rollback_report.rolled_back = true;
    result.rollback_report.restored_version = restored_version;
    result.rollback_report.reason = reason;

    StageReport rollback_report = kernel::make_stage_report("session_runtime.rollback");
    kernel::append_report_message(
        rollback_report,
        make_message(
            kernel::ReportSeverity::info,
            "runtime.rollback",
            reason));
    record_stage(result, "rollback", rollback_report, restored_version, restored_version);
}

HistoryEvent make_history_event(const CommandResult& result) {
    HistoryEvent event;
    event.command_id = result.command_id;
    event.accepted = result.accepted;
    event.status = result.user_visible_status;
    event.base_version = result.transaction_trace.base_version;
    event.new_state_version = result.new_state_version;
    event.transaction_trace = result.transaction_trace;
    event.stage_reports = result.stage_reports;
    return event;
}

}  // namespace

SessionRuntime::SessionRuntime(ModelSnapshot snapshot)
    : current_snapshot_(std::move(snapshot)) {}

void SessionRuntime::load_snapshot(ModelSnapshot snapshot) {
    current_snapshot_ = std::move(snapshot);
    history_.clear();
}

const ModelSnapshot& SessionRuntime::current_snapshot() const {
    return current_snapshot_;
}

const std::vector<HistoryEvent>& SessionRuntime::history() const {
    return history_;
}

CommandResult SessionRuntime::solve(SolveIntent intent) {
    return execute(make_solve_command(std::move(intent)));
}

CommandResult SessionRuntime::execute(const Command& command) {
    CommandResult result;
    result.command_id = command.id;
    result.new_state_version = current_snapshot_.state_version;
    result.transaction_trace.command_id = command.id;
    result.transaction_trace.base_version = current_snapshot_.state_version;
    result.transaction_trace.final_version = current_snapshot_.state_version;

    auto command_validation = validate_command(current_snapshot_, command);
    result.command_validation = command_validation.payload;
    record_stage(
        result,
        "command_validation",
        command_validation.report,
        current_snapshot_.state_version,
        current_snapshot_.state_version);
    if (!result.command_validation.valid) {
        result.user_visible_status = SolveStatus::unsupported;
        result.obstruction_report = diagnostics::make_obstruction(
            "runtime.command_rejected",
            "Runtime command failed precondition validation.");
        rollback(
            result,
            "Command rejected before transaction mutation.",
            current_snapshot_.state_version);
        history_.push_back(make_history_event(result));
        return result;
    }

    ModelSnapshot transaction_snapshot = current_snapshot_;
    transaction_snapshot.solve_intent = command.solve_intent;

    auto kernel_validation = kernel::validate_model(transaction_snapshot);
    record_stage(
        result,
        "model_validation",
        kernel_validation.report,
        transaction_snapshot.state_version,
        transaction_snapshot.state_version);
    if (kernel_validation.report.status == kernel::StageStatus::error) {
        result.user_visible_status = SolveStatus::invalid_model;
        result.obstruction_report = diagnostics::make_obstruction(
            "runtime.invalid_model",
            "Kernel model validation failed before planning.");
        rollback(result, "Model validation failed.", current_snapshot_.state_version);
        history_.push_back(make_history_event(result));
        return result;
    }

    StageReport validation_report = constraints::validate_model_constraints(transaction_snapshot);
    record_stage(
        result,
        "constraint_validation",
        validation_report,
        transaction_snapshot.state_version,
        transaction_snapshot.state_version);
    if (validation_report.status == kernel::StageStatus::error) {
        result.user_visible_status = SolveStatus::invalid_model;
        result.obstruction_report = diagnostics::make_obstruction(
            "runtime.invalid_constraints",
            "Constraint catalog validation failed before planning.");
        rollback(result, "Constraint validation failed.", current_snapshot_.state_version);
        history_.push_back(make_history_event(result));
        return result;
    }

    graph::IncidenceIndices incidence =
        graph::build_incidence_indices(graph::IncidenceInput{transaction_snapshot});
    record_stage(
        result,
        "incidence_index",
        incidence.report,
        transaction_snapshot.state_version,
        transaction_snapshot.state_version);
    if (incidence.report.status == kernel::StageStatus::error) {
        result.user_visible_status = SolveStatus::invalid_model;
        result.obstruction_report = diagnostics::make_obstruction(
            "runtime.invalid_incidence",
            "Incidence graph construction failed.");
        rollback(result, "Incidence graph construction failed.", current_snapshot_.state_version);
        history_.push_back(make_history_event(result));
        return result;
    }

    result.planner_output = planning::plan_decomposition(
        planning::PlannerInput{transaction_snapshot, incidence, command.solve_intent, {}});
    record_stage(
        result,
        "planning",
        result.planner_output.structural_report,
        transaction_snapshot.state_version,
        transaction_snapshot.state_version);

    kernel::ContextSnapshot root_context = kernel::make_whole_model_context(transaction_snapshot);
    diagnostics::DiagnosticInput pre_solve_input;
    pre_solve_input.phase = diagnostics::DiagnosticPhase::pre_solve;
    pre_solve_input.model = transaction_snapshot;
    pre_solve_input.context = root_context;
    pre_solve_input.gauge_policy = result.planner_output.gauge_policy;
    result.pre_solve_diagnostics = diagnostics::diagnose(pre_solve_input);
    StageReport pre_solve_report = kernel::make_stage_report("session_runtime.pre_solve_diagnostics");
    kernel::append_report_message(
        pre_solve_report,
        make_message(
            kernel::ReportSeverity::info,
            "runtime.pre_solve_diagnostics",
            "Pre-solve diagnostics completed."));
    record_stage(
        result,
        "pre_solve_diagnostics",
        pre_solve_report,
        transaction_snapshot.state_version,
        transaction_snapshot.state_version);

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
            rollback(result, "Planner produced a missing context.", current_snapshot_.state_version);
            history_.push_back(make_history_event(result));
            return result;
        }

        auto task = numeric::make_numeric_task(
            transaction_snapshot,
            *context,
            subproblem.active_variables,
            subproblem.active_equations,
            result.planner_output.gauge_policy);
        task.boundary_variables = subproblem.boundary_variables;

        auto numeric_report = numeric::solve_local(task);
        local_sections.push_back(numeric_report.local_section);
        record_stage(
            result,
            "numeric_solve",
            numeric_report.stage_report,
            transaction_snapshot.state_version,
            transaction_snapshot.state_version);
        result.numeric_reports.push_back(numeric_report);

        if (numeric_report.result_code != SolveStatus::solved) {
            result.user_visible_status = numeric_report.result_code;
            result.obstruction_report = diagnostics::make_obstruction(
                "runtime.numeric_failure",
                numeric_report.failure_cause.empty()
                    ? "Numeric engine failed."
                    : numeric_report.failure_cause);
            rollback(result, "Numeric engine failed.", current_snapshot_.state_version);
            history_.push_back(make_history_event(result));
            return result;
        }
    }

    result.gluing_report = diagnostics::glue_local_sections(
        diagnostics::GluingInput{
            transaction_snapshot,
            result.planner_output.cover_plan,
            local_sections,
            result.planner_output.boundary_projections,
            result.planner_output.gauge_policy,
            transaction_snapshot.tolerances});
    record_stage(
        result,
        "gluing",
        result.gluing_report.stage_report,
        transaction_snapshot.state_version,
        transaction_snapshot.state_version);

    if (!result.gluing_report.accepted) {
        result.user_visible_status = SolveStatus::inconsistent;
        result.obstruction_report = result.gluing_report.obstruction_report;
        rollback(result, "Gluing rejected the local sections.", current_snapshot_.state_version);
        history_.push_back(make_history_event(result));
        return result;
    }

    commit_accepted_state(result.gluing_report.proposed_global_state);
    result.accepted = true;
    result.new_state_version = current_snapshot_.state_version;
    result.transaction_trace.committed = true;
    result.transaction_trace.final_version = current_snapshot_.state_version;
    result.user_visible_status =
        result.pre_solve_diagnostics.status_code == SolveStatus::solved
            ? SolveStatus::solved
            : SolveStatus::accepted_with_warnings;
    StageReport commit_report = kernel::make_stage_report("session_runtime.commit");
    kernel::append_report_message(
        commit_report,
        make_message(
            kernel::ReportSeverity::info,
            "runtime.commit",
            "Runtime committed the verified proposed state."));
    record_stage(
        result,
        "commit",
        commit_report,
        transaction_snapshot.state_version,
        current_snapshot_.state_version,
        true);
    history_.push_back(make_history_event(result));
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

ReplayReport SessionRuntime::replay(ReplayRequest request) const {
    ReplayReport report;
    report.command_id = request.command_id;
    for (const auto& event : history_) {
        if (event.command_id == request.command_id) {
            report.found = true;
            report.accepted = event.accepted;
            report.status = event.status;
            report.transaction_trace = event.transaction_trace;
            report.stage_reports = event.stage_reports;
            return report;
        }
    }
    return report;
}

gcs::kernel::ContractResult<CommandValidationReport> validate_command(
    const ModelSnapshot& current_snapshot,
    const Command& command) {
    kernel::ContractResult<CommandValidationReport> result;
    result.report = kernel::make_stage_report("session_runtime.validate_command");

    if (command.kind != CommandKind::solve) {
        result.payload.valid = false;
        result.payload.supported_kind = false;
        auto message = make_message(
            kernel::ReportSeverity::error,
            "runtime.unsupported_command",
            "Only solve commands are supported by the current runtime contract.",
            {kernel::StableId{"command", command.id.value}});
        result.payload.messages.push_back(message);
        kernel::append_report_message(result.report, std::move(message));
    }

    if (command.id.value == 0) {
        result.payload.valid = false;
        result.payload.command_id_present = false;
        auto message = make_message(
            kernel::ReportSeverity::error,
            "runtime.missing_command_id",
            "Runtime commands must carry a nonzero command ID.");
        result.payload.messages.push_back(message);
        kernel::append_report_message(result.report, std::move(message));
    }

    if (!(command.model_edit_or_solve_request.state_version ==
          current_snapshot.state_version)) {
        result.payload.valid = false;
        result.payload.request_base_version_matches = false;
        auto message = make_message(
            kernel::ReportSeverity::error,
            "runtime.command_base_version_mismatch",
            "Command request base version must match the runtime snapshot.",
            {kernel::StableId{"state_version",
                              command.model_edit_or_solve_request.state_version.value},
             kernel::StableId{"state_version", current_snapshot.state_version.value}});
        result.payload.messages.push_back(message);
        kernel::append_report_message(result.report, std::move(message));
    }

    return result;
}

}
