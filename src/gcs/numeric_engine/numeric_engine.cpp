module;

#include <algorithm>
#include <string>
#include <vector>

module gcs.numeric_engine;

import gcs.kernel;
import gcs.constraint_catalog;

namespace gcs::numeric {

NumericTask makeNumericTask(const ModelSnapshot& model,
                            const ContextSnapshot& context,
                            const std::vector<EntityId>& activeVariables,
                            const std::vector<ConstraintId>& activeEquations,
                            const GaugePolicy& gaugePolicy) {
    NumericTask task;
    task.problemSnapshot = model;
    task.contextSnapshot = context;
    task.activeVariables = activeVariables;
    task.activeEquations = activeEquations;
    task.tolerances = model.tolerances;
    task.gaugePolicy = gaugePolicy;
    return task;
}

NumericReport solveLocal(const NumericTask& task) {
    NumericReport report;
    report.stageReport = makeStageReport("numeric_engine.solve_local");
    report.localSection.contextId = task.contextSnapshot.id;
    report.localSection.entityStates = captureEntityStates(task.problemSnapshot, task.activeVariables);
    report.localSection.valid = true;
    report.proposedState.baseVersion = task.problemSnapshot.stateVersion;
    report.proposedState.entityStates = report.localSection.entityStates;

    int equationDof = 0;
    for (ConstraintId constraintId : task.activeEquations) {
        const auto* constraint = findConstraint(task.problemSnapshot, constraintId);
        if (constraint == nullptr) {
            report.resultCode = SolveStatus::InvalidModel;
            report.localSection.valid = false;
            report.failureCause = "Numeric task references a missing constraint.";
            ReportMessage message;
            message.severity = ReportSeverity::Error;
            message.code = "numeric.missing_constraint";
            message.message = report.failureCause;
            message.constraintIds.push_back(constraintId);
            report.stageReport.messages.push_back(message);
            report.stageReport.status = StageStatus::Error;
            return report;
        }
        equationDof += constraints::genericDofEffect(constraint->kind);
    }

    int variableDof = 0;
    for (EntityId entityId : task.activeVariables) {
        const auto* entity = findEntity(task.problemSnapshot, entityId);
        if (entity == nullptr) {
            report.resultCode = SolveStatus::InvalidModel;
            report.localSection.valid = false;
            report.failureCause = "Numeric task references a missing entity.";
            ReportMessage message;
            message.severity = ReportSeverity::Error;
            message.code = "numeric.missing_entity";
            message.message = report.failureCause;
            message.entityIds.push_back(entityId);
            report.stageReport.messages.push_back(message);
            report.stageReport.status = StageStatus::Error;
            return report;
        }
        variableDof += geometryDof(entity->kind);
    }

    report.rankEstimate = std::min(equationDof, std::max(0, variableDof - task.gaugePolicy.removedDof));
    report.initialResidual = 0.0;
    report.finalResidual = 0.0;
    report.stepNorm = 0.0;
    report.conditionEstimate = 1.0;
    report.iterationCount = 0;
    report.resultCode = SolveStatus::Solved;

    ReportMessage message;
    message.severity = ReportSeverity::Info;
    message.code = "numeric.local_section.placeholder";
    message.message = "Baseline numeric engine produced an identity local section.";
    message.contextIds.push_back(task.contextSnapshot.id);
    report.stageReport.messages.push_back(message);

    return report;
}

}
