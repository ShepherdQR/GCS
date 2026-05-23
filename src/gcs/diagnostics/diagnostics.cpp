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

}  // namespace

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

DiagnosticOutput diagnose(const DiagnosticInput& input) {
    DiagnosticOutput output;
    ContextSnapshot context = input.context.value_or(kernel::make_whole_model_context(input.model));
    output.dof_report = analyze_dof(input.model, context, input.gauge_policy);
    output.status_code = output.dof_report.status;

    if (input.numeric_report.has_value()) {
        output.rank_report.numeric_rank_estimate = input.numeric_report->rank_estimate;
        output.rank_report.condition_estimate = input.numeric_report->condition_estimate;
        output.residual_report.total_residual = input.numeric_report->final_residual;
        output.residual_report.max_residual = input.numeric_report->final_residual;
        if (input.numeric_report->result_code != SolveStatus::solved) {
            output.status_code = input.numeric_report->result_code;
        }
    }

    output.rank_report.structural_rank_estimate = output.dof_report.equation_dof;
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
