module;

#include <algorithm>
#include <cmath>
#include <string>
#include <utility>
#include <vector>

module gcs.numeric_engine;

import gcs.kernel;
import gcs.constraint_catalog;

namespace gcs::numeric {

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

void append_message(StageReport& report,
                    std::vector<ReportMessage>& payload_messages,
                    kernel::ReportMessage message) {
    payload_messages.push_back(message);
    kernel::append_report_message(report, std::move(message));
}

bool positive_tolerances(const TolerancePolicy& tolerances) {
    return tolerances.residual > 0.0 &&
           tolerances.rank > 0.0 &&
           tolerances.boundary > 0.0;
}

bool valid_solve_limits(const SolveLimits& limits) {
    return limits.max_iterations >= 0 && limits.trust_region_radius > 0.0;
}

double residual_norm(const std::vector<double>& residuals) {
    double sum = 0.0;
    for (double residual : residuals) {
        sum += residual * residual;
    }
    return std::sqrt(sum);
}

}  // namespace

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

gcs::kernel::ContractResult<NumericTaskValidationReport> validate_task(
    const NumericTask& task) {
    kernel::ContractResult<NumericTaskValidationReport> result;
    result.report = kernel::make_stage_report("numeric_engine.validate_task");

    if (!(task.context_snapshot.state_version == task.problem_snapshot.state_version)) {
        result.payload.valid = false;
        result.payload.context_version_matches = false;
        append_message(
            result.report,
            result.payload.messages,
            make_message(
                kernel::ReportSeverity::error,
                "numeric.context_version_mismatch",
                "Numeric task context state version must match the problem snapshot.",
                {kernel::StableId{"context", task.context_snapshot.id.value}}));
    }

    if (!positive_tolerances(task.tolerances)) {
        result.payload.valid = false;
        result.payload.tolerances_valid = false;
        append_message(
            result.report,
            result.payload.messages,
            make_message(
                kernel::ReportSeverity::error,
                "numeric.invalid_tolerance",
                "Numeric task tolerances must be positive."));
    }

    if (!valid_solve_limits(task.solve_limits)) {
        result.payload.valid = false;
        result.payload.solve_limits_valid = false;
        append_message(
            result.report,
            result.payload.messages,
            make_message(
                kernel::ReportSeverity::error,
                "numeric.invalid_solve_limits",
                "Numeric task solve limits are invalid."));
    }

    for (EntityId entity_id : task.active_variables) {
        if (kernel::find_entity(task.problem_snapshot, entity_id) == nullptr) {
            result.payload.valid = false;
            result.payload.active_variables_exist = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "numeric.missing_entity",
                    "Numeric task references a missing active entity.",
                    {kernel::StableId{"entity", entity_id.value}}));
        }
        if (!kernel::contains_entity(task.context_snapshot.entity_ids, entity_id)) {
            result.payload.valid = false;
            result.payload.active_variables_within_context = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "numeric.entity_not_in_context",
                    "Numeric task active entity is not part of the task context.",
                    {kernel::StableId{"context", task.context_snapshot.id.value},
                     kernel::StableId{"entity", entity_id.value}}));
        }
    }

    for (ConstraintId constraint_id : task.active_equations) {
        if (kernel::find_constraint(task.problem_snapshot, constraint_id) == nullptr) {
            result.payload.valid = false;
            result.payload.active_equations_exist = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "numeric.missing_constraint",
                    "Numeric task references a missing active constraint.",
                    {kernel::StableId{"constraint", constraint_id.value}}));
        }
        if (!kernel::contains_constraint(task.context_snapshot.constraint_ids, constraint_id)) {
            result.payload.valid = false;
            result.payload.active_equations_within_context = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "numeric.constraint_not_in_context",
                    "Numeric task active constraint is not part of the task context.",
                    {kernel::StableId{"context", task.context_snapshot.id.value},
                     kernel::StableId{"constraint", constraint_id.value}}));
        }
    }

    for (EntityId entity_id : task.boundary_variables) {
        if (!kernel::contains_entity(task.active_variables, entity_id)) {
            result.payload.valid = false;
            result.payload.boundary_variables_are_active = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "numeric.boundary_not_active",
                    "Numeric task boundary variable must also be an active variable.",
                    {kernel::StableId{"entity", entity_id.value}}));
        }
    }

    return result;
}

gcs::kernel::ContractResult<EquationAssembly> assemble_equations(
    const NumericTask& task,
    const constraints::ConstraintCatalog& catalog) {
    kernel::ContractResult<EquationAssembly> result;
    result.report = kernel::make_stage_report("numeric_engine.assemble_equations");

    auto validation = validate_task(task);
    for (auto message : validation.report.messages) {
        kernel::append_report_message(result.report, std::move(message));
    }
    if (!validation.payload.valid) return result;

    result.payload.variable_order = task.active_variables;
    result.payload.equation_order = task.active_equations;
    for (EntityId entity_id : task.active_variables) {
        const auto* entity = kernel::find_entity(task.problem_snapshot, entity_id);
        if (entity != nullptr) {
            result.payload.variable_dimension += kernel::geometry_dof(entity->kind);
        }
    }

    int residual_offset = 0;
    for (ConstraintId constraint_id : task.active_equations) {
        auto residual = constraints::evaluate_residual(
            catalog,
            constraints::ResidualEvaluationRequest{task.problem_snapshot, constraint_id});
        for (auto message : residual.report.messages) {
            kernel::append_report_message(result.report, std::move(message));
        }
        if (!residual.payload.valid) {
            kernel::append_report_message(
                result.report,
                make_message(
                    kernel::ReportSeverity::error,
                    "numeric.residual_assembly_failed",
                    "Constraint residual evaluation failed during numeric assembly.",
                    {kernel::StableId{"constraint", constraint_id.value}}));
            return result;
        }

        ResidualBlock block;
        block.constraint_id = constraint_id;
        block.offset = residual_offset;
        block.dimension = static_cast<int>(residual.payload.residuals.size());
        block.residuals = residual.payload.residuals;
        residual_offset += block.dimension;
        result.payload.residual_dimension += block.dimension;
        for (double value : block.residuals) {
            result.payload.residual_vector.push_back(value);
        }
        result.payload.residual_blocks.push_back(std::move(block));
    }

    result.payload.valid = true;
    return result;
}

gcs::kernel::ContractResult<EquationAssembly> assemble_equations(const NumericTask& task) {
    return assemble_equations(task, constraints::builtin_catalog());
}

NumericReport solve_local(const NumericTask& task) {
    NumericReport report;
    report.stage_report = kernel::make_stage_report("numeric_engine.solve_local");
    report.local_section.context_id = task.context_snapshot.id;
    report.proposed_state.base_version = task.problem_snapshot.state_version;

    auto assembly = assemble_equations(task);
    for (auto message : assembly.report.messages) {
        kernel::append_report_message(report.stage_report, std::move(message));
    }
    if (!assembly.payload.valid) {
        report.result_code = SolveStatus::invalid_model;
        report.local_section.valid = false;
        report.failure_cause = "Numeric task validation or equation assembly failed.";
        return report;
    }

    report.local_section.entity_states = kernel::capture_entity_states(
        task.problem_snapshot,
        task.active_variables);
    report.local_section.valid = true;
    report.proposed_state.entity_states = report.local_section.entity_states;

    report.rank_estimate = std::min(
        assembly.payload.residual_dimension,
        std::max(0, assembly.payload.variable_dimension - task.gauge_policy.removed_dof));
    report.initial_residual = residual_norm(assembly.payload.residual_vector);
    report.final_residual = report.initial_residual;
    report.step_norm = 0.0;
    report.condition_estimate = 1.0;
    report.iteration_count = 0;
    report.result_code = SolveStatus::solved;

    kernel::append_report_message(
        report.stage_report,
        kernel::make_report_message(
            kernel::ReportSeverity::info,
            kernel::ReportCode{"numeric.local_section.placeholder"},
            "Baseline numeric engine assembled equations and produced an identity local section.",
            {kernel::StableId{"context", task.context_snapshot.id.value}}));

    return report;
}

}
