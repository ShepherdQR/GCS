module;

#include <vector>

module gcs.decomposition_planner;

import gcs.kernel;
import gcs.incidence_graph;

namespace gcs::planning {

namespace {

int computeExpectedFreeDof(const ModelSnapshot& model,
                           const std::vector<EntityId>& entityIds,
                           const std::vector<ConstraintId>& constraintIds,
                           int gaugeDof) {
    int parameterDof = 0;
    for (EntityId entityId : entityIds) {
        if (const auto* entity = findEntity(model, entityId)) {
            parameterDof += geometryDof(entity->kind);
        }
    }

    int equationDof = 0;
    for (ConstraintId constraintId : constraintIds) {
        if (const auto* constraint = findConstraint(model, constraintId)) {
            equationDof += constraintDofEffect(constraint->kind);
        }
    }

    return parameterDof - equationDof - gaugeDof;
}

}

PlannerOutput planDecomposition(const PlannerInput& input) {
    PlannerOutput output;
    output.structuralReport = makeStageReport("decomposition_planner.plan");
    output.coverPlan.id = CoverId{1};
    output.coverPlan.rootContextId = ContextId{0};
    output.gaugePolicy = GaugePolicy{GaugeKind::None, ContextId{0}, {}, 0};

    ContextSnapshot root = makeWholeModelContext(input.model, ContextId{0});
    output.coverPlan.contexts.push_back(root);

    const bool splitIntoComponents = input.incidence.connectedComponents.size() > 1;
    if (!splitIntoComponents) {
        Subproblem subproblem;
        subproblem.id = 0;
        subproblem.contextId = root.id;
        subproblem.activeVariables = root.entityIds;
        subproblem.activeEquations = root.constraintIds;
        subproblem.expectedFreeDof = computeExpectedFreeDof(
            input.model,
            subproblem.activeVariables,
            subproblem.activeEquations,
            output.gaugePolicy.removedDof);
        output.subproblems.push_back(subproblem);
        output.solveOrder.push_back(SolveStep{0, root.id});
        return output;
    }

    int nextContextId = 1;
    int subproblemId = 0;
    for (const auto& component : input.incidence.connectedComponents) {
        ContextSnapshot context;
        context.id = ContextId{nextContextId++};
        context.kind = ContextKind::ConnectedComponent;
        context.entityIds = component.entityIds;
        context.constraintIds = component.constraintIds;
        context.rigidSetIds = component.rigidSetIds;
        output.coverPlan.contexts.push_back(context);

        Subproblem subproblem;
        subproblem.id = subproblemId;
        subproblem.contextId = context.id;
        subproblem.activeVariables = context.entityIds;
        subproblem.activeEquations = context.constraintIds;
        subproblem.expectedFreeDof = computeExpectedFreeDof(
            input.model,
            subproblem.activeVariables,
            subproblem.activeEquations,
            output.gaugePolicy.removedDof);
        output.subproblems.push_back(subproblem);
        output.solveOrder.push_back(SolveStep{subproblemId, context.id});
        ++subproblemId;
    }

    if (output.subproblems.empty()) {
        output.structuralReport.status = StageStatus::Warning;
        ReportMessage message;
        message.severity = ReportSeverity::Warning;
        message.code = "planner.empty_model";
        message.message = "No subproblems were produced for an empty model.";
        output.structuralReport.messages.push_back(message);
    }

    return output;
}

}
