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

SessionRuntime::SessionRuntime(ModelSnapshot snapshot)
    : currentSnapshot_(std::move(snapshot)) {}

void SessionRuntime::loadSnapshot(ModelSnapshot snapshot) {
    currentSnapshot_ = std::move(snapshot);
}

const ModelSnapshot& SessionRuntime::currentSnapshot() const {
    return currentSnapshot_;
}

CommandResult SessionRuntime::solve(SolveIntent intent) {
    return execute(makeSolveCommand(std::move(intent)));
}

CommandResult SessionRuntime::execute(const Command& command) {
    CommandResult result;
    if (command.kind != CommandKind::Solve) {
        result.userVisibleStatus = SolveStatus::Unsupported;
        result.obstructionReport = diagnostics::makeObstruction(
            "runtime.unsupported_command",
            "Only solve commands are supported by the first runtime skeleton.");
        return result;
    }

    currentSnapshot_.solveIntent = command.solveIntent;

    StageReport validationReport = constraints::validateModelConstraints(currentSnapshot_);
    result.stageReports.push_back(validationReport);
    if (validationReport.status == StageStatus::Error) {
        result.userVisibleStatus = SolveStatus::InvalidModel;
        result.obstructionReport = diagnostics::makeObstruction(
            "runtime.invalid_model",
            "Constraint catalog validation failed before planning.");
        return result;
    }

    graph::IncidenceIndices incidence = graph::buildIncidenceIndices(graph::IncidenceInput{currentSnapshot_});
    result.stageReports.push_back(incidence.report);
    if (incidence.report.status == StageStatus::Error) {
        result.userVisibleStatus = SolveStatus::InvalidModel;
        result.obstructionReport = diagnostics::makeObstruction(
            "runtime.invalid_incidence",
            "Incidence graph construction failed.");
        return result;
    }

    result.plannerOutput = planning::planDecomposition(
        planning::PlannerInput{currentSnapshot_, incidence, command.solveIntent, {}});
    result.stageReports.push_back(result.plannerOutput.structuralReport);

    ContextSnapshot rootContext = makeWholeModelContext(currentSnapshot_);
    result.preSolveDiagnostics = diagnostics::diagnose(
        diagnostics::DiagnosticInput{
            currentSnapshot_,
            rootContext,
            {},
            result.plannerOutput.gaugePolicy});

    std::vector<LocalSection> localSections;
    for (const auto& subproblem : result.plannerOutput.subproblems) {
        const ContextSnapshot* context = nullptr;
        for (const auto& candidate : result.plannerOutput.coverPlan.contexts) {
            if (candidate.id == subproblem.contextId) {
                context = &candidate;
                break;
            }
        }
        if (context == nullptr) {
            result.userVisibleStatus = SolveStatus::InvalidModel;
            result.obstructionReport = diagnostics::makeObstruction(
                "runtime.missing_context",
                "Planner produced a subproblem whose context is absent from the cover plan.");
            return result;
        }

        auto task = numeric::makeNumericTask(
            currentSnapshot_,
            *context,
            subproblem.activeVariables,
            subproblem.activeEquations,
            result.plannerOutput.gaugePolicy);
        task.boundaryVariables = subproblem.boundaryVariables;

        auto numericReport = numeric::solveLocal(task);
        localSections.push_back(numericReport.localSection);
        result.stageReports.push_back(numericReport.stageReport);
        result.numericReports.push_back(numericReport);

        if (numericReport.resultCode != SolveStatus::Solved) {
            result.userVisibleStatus = numericReport.resultCode;
            result.obstructionReport = diagnostics::makeObstruction(
                "runtime.numeric_failure",
                numericReport.failureCause.empty() ? "Numeric engine failed." : numericReport.failureCause);
            return result;
        }
    }

    result.gluingReport = diagnostics::glueLocalSections(
        diagnostics::GluingInput{
            currentSnapshot_,
            result.plannerOutput.coverPlan,
            localSections,
            result.plannerOutput.boundaryProjections,
            result.plannerOutput.gaugePolicy,
            currentSnapshot_.tolerances});
    result.stageReports.push_back(result.gluingReport.stageReport);

    if (!result.gluingReport.accepted) {
        result.userVisibleStatus = SolveStatus::Inconsistent;
        result.obstructionReport = result.gluingReport.obstructionReport;
        return result;
    }

    commitAcceptedState(result.gluingReport.proposedGlobalState);
    result.accepted = true;
    result.newStateVersion = currentSnapshot_.stateVersion;
    result.userVisibleStatus = result.preSolveDiagnostics.statusCode == SolveStatus::Solved
        ? SolveStatus::Solved
        : SolveStatus::AcceptedWithWarnings;
    return result;
}

Command SessionRuntime::makeSolveCommand(SolveIntent intent) {
    Command command;
    command.id = nextCommandId_;
    nextCommandId_ = CommandId{nextCommandId_.value + 1};
    command.kind = CommandKind::Solve;
    command.solveIntent = std::move(intent);
    command.modelEditOrSolveRequest = currentSnapshot_;
    return command;
}

void SessionRuntime::commitAcceptedState(const ProposedState& proposedState) {
    for (const auto& state : proposedState.entityStates) {
        for (auto& entity : currentSnapshot_.entities) {
            if (entity.id == state.entityId) {
                entity.parameters = state.parameters;
                break;
            }
        }
    }
    currentSnapshot_.stateVersion = nextVersion(currentSnapshot_.stateVersion);
}

}
