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

namespace {

bool sameParameters(const ParameterBlock& lhs, const ParameterBlock& rhs, double tolerance) {
    const int dimension = lhs.dimension < rhs.dimension ? lhs.dimension : rhs.dimension;
    for (int i = 0; i < dimension; ++i) {
        if (std::abs(lhs.values[static_cast<std::size_t>(i)] -
                     rhs.values[static_cast<std::size_t>(i)]) > tolerance) {
            return false;
        }
    }
    return true;
}

EntityState* findState(std::vector<EntityState>& states, EntityId entityId) {
    for (auto& state : states) {
        if (state.entityId == entityId) return &state;
    }
    return nullptr;
}

SolveStatus classifyFreeDof(int freeDof) {
    if (freeDof > 0) return SolveStatus::UnderConstrained;
    if (freeDof < 0) return SolveStatus::OverConstrained;
    return SolveStatus::Solved;
}

}

DofReport analyzeDof(const ModelSnapshot& model,
                     const ContextSnapshot& context,
                     const GaugePolicy& gaugePolicy) {
    DofReport report;
    report.gaugeDof = gaugePolicy.removedDof;
    for (EntityId entityId : context.entityIds) {
        if (const auto* entity = findEntity(model, entityId)) {
            report.parameterDof += geometryDof(entity->kind);
        }
    }
    for (ConstraintId constraintId : context.constraintIds) {
        if (const auto* constraint = findConstraint(model, constraintId)) {
            report.equationDof += constraintDofEffect(constraint->kind);
        }
    }
    report.freeDof = report.parameterDof - report.equationDof - report.gaugeDof;
    report.status = classifyFreeDof(report.freeDof);
    return report;
}

DiagnosticOutput diagnose(const DiagnosticInput& input) {
    DiagnosticOutput output;
    ContextSnapshot context = input.context.value_or(makeWholeModelContext(input.model));
    output.dofReport = analyzeDof(input.model, context, input.gaugePolicy);
    output.statusCode = output.dofReport.status;

    if (input.numericReport.has_value()) {
        output.rankReport.numericRankEstimate = input.numericReport->rankEstimate;
        output.rankReport.conditionEstimate = input.numericReport->conditionEstimate;
        output.residualReport.totalResidual = input.numericReport->finalResidual;
        output.residualReport.maxResidual = input.numericReport->finalResidual;
        if (input.numericReport->resultCode != SolveStatus::Solved) {
            output.statusCode = input.numericReport->resultCode;
        }
    }

    output.rankReport.structuralRankEstimate = output.dofReport.equationDof;
    return output;
}

GluingReport glueLocalSections(const GluingInput& input) {
    GluingReport report;
    report.stageReport = makeStageReport("diagnostics.glue_local_sections");
    report.proposedGlobalState.baseVersion = input.model.stateVersion;

    for (const auto& section : input.localSections) {
        if (!section.valid) {
            report.accepted = false;
            report.obstructionReport = makeObstruction(
                "gluing.invalid_local_section",
                "At least one local section was marked invalid by its producer.");
            report.obstructionReport.contextIds.push_back(section.contextId);
            report.stageReport.status = StageStatus::Error;
            return report;
        }

        for (const auto& state : section.entityStates) {
            if (auto* existing = findState(report.proposedGlobalState.entityStates, state.entityId)) {
                if (!sameParameters(existing->parameters, state.parameters, input.tolerances.boundary)) {
                    report.accepted = false;
                    report.obstructionReport = makeObstruction(
                        "gluing.entity_state_mismatch",
                        "Local sections disagree on a shared entity state.");
                    report.obstructionReport.contextIds.push_back(section.contextId);
                    report.obstructionReport.entityIds.push_back(state.entityId);
                    report.stageReport.status = StageStatus::Error;
                    return report;
                }
            } else {
                report.proposedGlobalState.entityStates.push_back(state);
            }
        }
    }

    for (const auto& projection : input.boundaryProjections) {
        OverlapStatus status;
        status.projectionId = projection.id;
        status.compatible = true;
        status.boundaryResidual = 0.0;
        status.entityIds = projection.entityIds;
        report.overlapStatuses.push_back(status);
    }

    report.gaugeConsistent = true;
    report.accepted = true;
    ReportMessage message;
    message.severity = ReportSeverity::Info;
    message.code = "gluing.accepted";
    message.message = "All local sections are compatible within boundary tolerance.";
    report.stageReport.messages.push_back(message);
    return report;
}

ObstructionReport makeObstruction(std::string code, std::string message) {
    ObstructionReport obstruction;
    obstruction.present = true;
    obstruction.code = std::move(code);
    obstruction.message = std::move(message);
    return obstruction;
}

}
