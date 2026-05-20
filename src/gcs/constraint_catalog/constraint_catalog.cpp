module;

#include <string>
#include <utility>
#include <vector>

module gcs.constraint_catalog;

import gcs.kernel;

namespace gcs::constraints {

namespace {

ReportMessage makeMessage(ReportSeverity severity, std::string code, std::string message,
                          ConstraintId constraintId) {
    ReportMessage reportMessage;
    reportMessage.severity = severity;
    reportMessage.code = std::move(code);
    reportMessage.message = std::move(message);
    reportMessage.constraintIds.push_back(constraintId);
    return reportMessage;
}

}

const std::vector<ConstraintDefinition>& builtinDefinitions() {
    static const std::vector<ConstraintDefinition> definitions = {
        {ConstraintKind::Coincident, "Coincident", 2, 2, 3, 3, true},
        {ConstraintKind::Parallel, "Parallel", 2, 2, 2, 2, true},
        {ConstraintKind::Perpendicular, "Perpendicular", 2, 2, 1, 1, true},
        {ConstraintKind::Distance, "Distance", 2, 2, 1, 1, true},
        {ConstraintKind::Angle, "Angle", 2, 2, 1, 1, true},
    };
    return definitions;
}

const ConstraintDefinition* findDefinition(ConstraintKind kind) {
    for (const auto& definition : builtinDefinitions()) {
        if (definition.kind == kind) return &definition;
    }
    return nullptr;
}

int residualDimension(ConstraintKind kind) {
    if (const auto* definition = findDefinition(kind)) {
        return definition->residualDimension;
    }
    return 0;
}

int genericDofEffect(ConstraintKind kind) {
    if (const auto* definition = findDefinition(kind)) {
        return definition->genericDofEffect;
    }
    return 0;
}

ConstraintValidationResult validateConstraint(const ConstraintValidationInput& input) {
    ConstraintValidationResult result;
    const auto* definition = findDefinition(input.constraint.kind);
    if (definition == nullptr) {
        result.messages.push_back(makeMessage(
            ReportSeverity::Error,
            "constraint.unsupported_kind",
            "Constraint kind is not registered in the constraint catalog.",
            input.constraint.id));
        return result;
    }

    result.definition = *definition;
    result.valid = true;

    const auto entityCount = static_cast<int>(input.constraint.entityIds.size());
    if (entityCount < definition->minEntityCount || entityCount > definition->maxEntityCount) {
        result.valid = false;
        result.messages.push_back(makeMessage(
            ReportSeverity::Error,
            "constraint.invalid_arity",
            "Constraint entity count does not match its catalog signature.",
            input.constraint.id));
    }

    std::vector<RigidSetId> referencedRigidSets;
    for (EntityId entityId : input.constraint.entityIds) {
        const auto* entity = findEntity(input.model, entityId);
        if (entity == nullptr) {
            result.valid = false;
            auto message = makeMessage(
                ReportSeverity::Error,
                "constraint.missing_entity",
                "Constraint references an entity that is not present in the model.",
                input.constraint.id);
            message.entityIds.push_back(entityId);
            result.messages.push_back(message);
            continue;
        }

        if (definition->requiresDistinctRigidSets &&
            containsRigidSet(referencedRigidSets, entity->rigidSetId)) {
            result.valid = false;
            auto message = makeMessage(
                ReportSeverity::Error,
                "constraint.same_rigid_set",
                "Constraint endpoints must belong to distinct rigid sets.",
                input.constraint.id);
            message.entityIds.push_back(entityId);
            result.messages.push_back(message);
        }
        referencedRigidSets.push_back(entity->rigidSetId);
    }

    return result;
}

StageReport validateModelConstraints(const ModelSnapshot& model) {
    StageReport report = makeStageReport("constraint_catalog.validate_model");
    for (const auto& constraint : model.constraints) {
        auto validation = validateConstraint(ConstraintValidationInput{model, constraint});
        for (const auto& message : validation.messages) {
            report.messages.push_back(message);
        }
        if (!validation.valid) {
            report.status = StageStatus::Error;
        }
    }
    return report;
}

}
