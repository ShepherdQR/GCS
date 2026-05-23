module;

#include <cmath>
#include <cstddef>
#include <optional>
#include <string>
#include <utility>
#include <vector>

module gcs.diagnostics;

import gcs.kernel;
import gcs.numeric_engine;

namespace gcs::diagnostics {

namespace kernel = gcs::kernel;

namespace {

bool same_parameters(const kernel::ParameterVector& lhs,
                     const kernel::ParameterVector& rhs,
                     double tolerance) {
    const int dimension = lhs.dimension < rhs.dimension ? lhs.dimension : rhs.dimension;
    for (int i = 0; i < dimension; ++i) {
        if (std::abs(lhs.values[static_cast<std::size_t>(i)] -
                     rhs.values[static_cast<std::size_t>(i)]) > tolerance) {
            return false;
        }
    }
    return true;
}

kernel::EntityState* find_state(std::vector<kernel::EntityState>& states,
                                EntityId entity_id) {
    for (auto& state : states) {
        if (state.entity_id == entity_id) return &state;
    }
    return nullptr;
}

SolveStatus classify_free_dof(int free_dof) {
    if (free_dof > 0) return SolveStatus::under_constrained;
    if (free_dof < 0) return SolveStatus::over_constrained;
    return SolveStatus::solved;
}

int status_priority(SolveStatus status) {
    switch (status) {
        case SolveStatus::invalid_model: return 100;
        case SolveStatus::failed: return 95;
        case SolveStatus::inconsistent: return 90;
        case SolveStatus::numerically_singular: return 80;
        case SolveStatus::unsupported: return 75;
        case SolveStatus::over_constrained: return 70;
        case SolveStatus::under_constrained: return 60;
        case SolveStatus::redundant: return 50;
        case SolveStatus::accepted_with_warnings: return 40;
        case SolveStatus::solved: return 10;
        case SolveStatus::not_run: return 0;
    }
    return 0;
}

StatusEvidence make_evidence(SolveStatus status,
                             std::string source,
                             std::string code) {
    StatusEvidence evidence;
    evidence.status = status;
    evidence.source = std::move(source);
    evidence.code = std::move(code);
    evidence.priority = status_priority(status);
    return evidence;
}

}  // namespace

gcs::kernel::ContractResult<DofReport> analyze_dof(DofAnalysisRequest request) {
    kernel::ContractResult<DofReport> result;
    result.report = kernel::make_stage_report("diagnostics.analyze_dof");
    result.payload = analyze_dof(
        request.model,
        request.context,
        request.gauge_policy);
    return result;
}

DofReport analyze_dof(const ModelSnapshot& model,
                      const ContextSnapshot& context,
                      const GaugePolicy& gauge_policy) {
    DofReport report;
    report.gauge_dof = gauge_policy.removed_dof;
    for (EntityId entity_id : context.entity_ids) {
        if (const auto* entity = kernel::find_entity(model, entity_id)) {
            report.parameter_dof += kernel::geometry_dof(entity->kind);
        }
    }
    for (ConstraintId constraint_id : context.constraint_ids) {
        if (const auto* constraint = kernel::find_constraint(model, constraint_id)) {
            report.equation_dof += kernel::constraint_dof_effect(constraint->kind);
        }
    }
    report.free_dof = report.parameter_dof - report.equation_dof - report.gauge_dof;
    report.status = classify_free_dof(report.free_dof);
    return report;
}

gcs::kernel::ContractResult<ResidualReport> analyze_residuals(
    ResidualAnalysisRequest request) {
    kernel::ContractResult<ResidualReport> result;
    result.report = kernel::make_stage_report("diagnostics.analyze_residuals");

    if (!request.numeric_report.has_value()) {
        return result;
    }

    const auto& numeric_report = *request.numeric_report;
    result.payload.from_numeric_report = true;
    result.payload.residual_dimension = numeric_report.residual_report.dimension;
    result.payload.total_residual = numeric_report.residual_report.norm;
    result.payload.max_residual = numeric_report.residual_report.max_abs_value;
    result.payload.within_tolerance =
        result.payload.max_residual <= request.tolerances.residual;

    for (const auto& block : numeric_report.residual_report.blocks) {
        ConstraintResidual residual;
        residual.constraint_id = block.constraint_id;
        residual.dimension = block.dimension;
        residual.residual = block.norm;
        residual.max_abs_value = block.max_abs_value;
        residual.tolerance = request.tolerances.residual;
        residual.satisfied = block.max_abs_value <= request.tolerances.residual;
        result.payload.constraints.push_back(residual);
    }

    if (!result.payload.within_tolerance) {
        kernel::append_report_message(
            result.report,
            kernel::make_report_message(
                kernel::ReportSeverity::warning,
                kernel::ReportCode{"diagnostics.residual_out_of_tolerance"},
                "Numeric residual evidence exceeds the active residual tolerance."));
    }

    return result;
}

gcs::kernel::ContractResult<StatusPrecedenceTrace> resolve_status(
    StatusPrecedenceInput input) {
    kernel::ContractResult<StatusPrecedenceTrace> result;
    result.report = kernel::make_stage_report("diagnostics.resolve_status");

    if (input.evidence.empty()) {
        input.evidence.push_back(make_evidence(
            SolveStatus::solved,
            "diagnostics",
            "diagnostics.no_negative_evidence"));
    }

    int best_priority = -1;
    SolveStatus resolved = SolveStatus::not_run;
    for (auto evidence : input.evidence) {
        if (evidence.priority == 0) {
            evidence.priority = status_priority(evidence.status);
        }
        if (evidence.priority > best_priority) {
            best_priority = evidence.priority;
            resolved = evidence.status;
        }
        result.payload.considered.push_back(std::move(evidence));
    }

    result.payload.resolved_status = resolved;
    return result;
}

DiagnosticOutput diagnose(const DiagnosticInput& input) {
    DiagnosticOutput output;
    output.phase = input.phase;
    ContextSnapshot context = input.context.value_or(kernel::make_whole_model_context(input.model));
    auto dof = analyze_dof(DofAnalysisRequest{input.model, context, input.gauge_policy});
    output.dof_report = dof.payload;
    output.rank_report.structural_rank_estimate = output.dof_report.equation_dof;

    std::vector<StatusEvidence> evidence;
    evidence.push_back(make_evidence(
        output.dof_report.status,
        "diagnostics.dof",
        "diagnostics.structural_dof_status"));

    if (input.numeric_report.has_value()) {
        const auto& numeric_report = *input.numeric_report;
        output.rank_report.numeric_rank_estimate =
            numeric_report.rank_condition_report.rank_estimate;
        output.rank_report.numeric_variable_dimension =
            numeric_report.rank_condition_report.variable_dimension;
        output.rank_report.numeric_residual_dimension =
            numeric_report.rank_condition_report.residual_dimension;
        output.rank_report.numeric_nullity_estimate =
            numeric_report.rank_condition_report.nullity_estimate;
        output.rank_report.numeric_under_constrained =
            numeric_report.rank_condition_report.under_constrained;
        output.rank_report.numeric_over_constrained =
            numeric_report.rank_condition_report.over_constrained;
        output.rank_report.numeric_singular =
            numeric_report.rank_condition_report.numerically_singular;
        output.rank_report.condition_estimate_available =
            numeric_report.rank_condition_report.condition_estimate_available;
        output.rank_report.condition_estimate =
            numeric_report.rank_condition_report.condition_estimate;

        auto residuals = analyze_residuals(
            ResidualAnalysisRequest{
                input.model,
                context,
                input.numeric_report,
                input.model.tolerances});
        output.residual_report = residuals.payload;

        if (input.numeric_report->result_code != SolveStatus::solved) {
            evidence.push_back(make_evidence(
                input.numeric_report->result_code,
                "numeric_engine",
                "diagnostics.numeric_result_status"));
        }
        if (output.rank_report.numeric_singular) {
            evidence.push_back(make_evidence(
                SolveStatus::numerically_singular,
                "diagnostics.rank",
                "diagnostics.numeric_rank_singular"));
        }
        if (output.rank_report.numeric_over_constrained) {
            evidence.push_back(make_evidence(
                SolveStatus::over_constrained,
                "diagnostics.rank",
                "diagnostics.numeric_rank_over_constrained"));
        }
        if (output.rank_report.numeric_under_constrained) {
            evidence.push_back(make_evidence(
                SolveStatus::under_constrained,
                "diagnostics.rank",
                "diagnostics.numeric_rank_under_constrained"));
        }
        if (output.residual_report.from_numeric_report &&
            !output.residual_report.within_tolerance) {
            evidence.push_back(make_evidence(
                SolveStatus::inconsistent,
                "diagnostics.residual",
                "diagnostics.residual_out_of_tolerance"));
        }
    }

    auto precedence = resolve_status(StatusPrecedenceInput{std::move(evidence)});
    output.status_precedence_trace = precedence.payload;
    output.status_code = output.status_precedence_trace.resolved_status;
    return output;
}

GluingReport glue_local_sections(const GluingInput& input) {
    GluingReport report;
    report.stage_report = kernel::make_stage_report("diagnostics.glue_local_sections");
    report.proposed_global_state.base_version = input.model.state_version;

    for (const auto& section : input.local_sections) {
        if (!section.valid) {
            report.accepted = false;
            report.obstruction_report = make_obstruction(
                "gluing.invalid_local_section",
                "At least one local section was marked invalid by its producer.");
            report.obstruction_report.context_ids.push_back(section.context_id);
            report.stage_report.status = kernel::StageStatus::error;
            return report;
        }

        for (const auto& state : section.entity_states) {
            if (auto* existing =
                    find_state(report.proposed_global_state.entity_states, state.entity_id)) {
                if (!same_parameters(existing->parameters,
                                     state.parameters,
                                     input.tolerances.boundary)) {
                    report.accepted = false;
                    report.obstruction_report = make_obstruction(
                        "gluing.entity_state_mismatch",
                        "Local sections disagree on a shared entity state.");
                    report.obstruction_report.context_ids.push_back(section.context_id);
                    report.obstruction_report.entity_ids.push_back(state.entity_id);
                    report.stage_report.status = kernel::StageStatus::error;
                    return report;
                }
            } else {
                report.proposed_global_state.entity_states.push_back(state);
            }
        }
    }

    for (const auto& projection : input.boundary_projections) {
        OverlapStatus status;
        status.projection_id = projection.id;
        status.compatible = true;
        status.boundary_residual = 0.0;
        status.entity_ids = projection.entity_ids;
        report.overlap_statuses.push_back(status);
    }

    report.gauge_consistent = true;
    report.accepted = true;
    kernel::append_report_message(
        report.stage_report,
        kernel::make_report_message(
            kernel::ReportSeverity::info,
            kernel::ReportCode{"gluing.accepted"},
            "All local sections are compatible within boundary tolerance."));
    return report;
}

ObstructionReport make_obstruction(std::string code, std::string message) {
    ObstructionReport obstruction;
    obstruction.present = true;
    obstruction.code = std::move(code);
    obstruction.message = std::move(message);
    return obstruction;
}

}
