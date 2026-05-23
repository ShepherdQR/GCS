module;

#include <string>
#include <utility>
#include <vector>

module gcs.constraint_catalog;

import gcs.kernel;

namespace gcs::constraints {

namespace kernel = gcs::kernel;

namespace {

kernel::StableId constraint_subject(ConstraintId id) {
    return kernel::StableId{"constraint", id.value};
}

kernel::StableId entity_subject(kernel::EntityId id) {
    return kernel::StableId{"entity", id.value};
}

ReportMessage make_message(kernel::ReportSeverity severity,
                           std::string code,
                           std::string summary,
                           ConstraintId constraint_id) {
    return kernel::make_report_message(
        severity,
        kernel::ReportCode{std::move(code)},
        std::move(summary),
        {constraint_subject(constraint_id)});
}

}  // namespace

const std::vector<ConstraintDefinition>& builtin_definitions() {
    static const std::vector<ConstraintDefinition> definitions = {
        {ConstraintKind::coincident, "Coincident", 2, 2, 3, 3, true},
        {ConstraintKind::parallel, "Parallel", 2, 2, 2, 2, true},
        {ConstraintKind::perpendicular, "Perpendicular", 2, 2, 1, 1, true},
        {ConstraintKind::distance, "Distance", 2, 2, 1, 1, true},
        {ConstraintKind::angle, "Angle", 2, 2, 1, 1, true},
    };
    return definitions;
}

const ConstraintDefinition* find_definition(ConstraintKind kind) {
    for (const auto& definition : builtin_definitions()) {
        if (definition.kind == kind) return &definition;
    }
    return nullptr;
}

int residual_dimension(ConstraintKind kind) {
    if (const auto* definition = find_definition(kind)) {
        return definition->residual_dimension;
    }
    return 0;
}

int generic_dof_effect(ConstraintKind kind) {
    if (const auto* definition = find_definition(kind)) {
        return definition->generic_dof_effect;
    }
    return 0;
}

ConstraintValidationResult validate_constraint(const ConstraintValidationInput& input) {
    ConstraintValidationResult result;
    const auto* definition = find_definition(input.constraint.kind);
    if (definition == nullptr) {
        result.messages.push_back(make_message(
            kernel::ReportSeverity::error,
            "constraint.unsupported_kind",
            "Constraint kind is not registered in the constraint catalog.",
            input.constraint.id));
        return result;
    }

    result.definition = *definition;
    result.valid = true;

    const auto entity_count = static_cast<int>(input.constraint.entity_ids.size());
    if (entity_count < definition->min_entity_count ||
        entity_count > definition->max_entity_count) {
        result.valid = false;
        result.messages.push_back(make_message(
            kernel::ReportSeverity::error,
            "constraint.invalid_arity",
            "Constraint entity count does not match its catalog signature.",
            input.constraint.id));
    }

    std::vector<kernel::RigidSetId> referenced_rigid_sets;
    for (kernel::EntityId entity_id : input.constraint.entity_ids) {
        const auto* entity = kernel::find_entity(input.model, entity_id);
        if (entity == nullptr) {
            result.valid = false;
            auto message = make_message(
                kernel::ReportSeverity::error,
                "constraint.missing_entity",
                "Constraint references an entity that is not present in the model.",
                input.constraint.id);
            message.subjects.push_back(entity_subject(entity_id));
            result.messages.push_back(std::move(message));
            continue;
        }

        if (definition->requires_distinct_rigid_sets &&
            kernel::contains_rigid_set(referenced_rigid_sets, entity->rigid_set_id)) {
            result.valid = false;
            auto message = make_message(
                kernel::ReportSeverity::error,
                "constraint.same_rigid_set",
                "Constraint endpoints must belong to distinct rigid sets.",
                input.constraint.id);
            message.subjects.push_back(entity_subject(entity_id));
            result.messages.push_back(std::move(message));
        }
        referenced_rigid_sets.push_back(entity->rigid_set_id);
    }

    return result;
}

StageReport validate_model_constraints(const ModelSnapshot& model) {
    StageReport report = kernel::make_stage_report("constraint_catalog.validate_model");
    for (const auto& constraint : model.constraints) {
        auto validation = validate_constraint(ConstraintValidationInput{model, constraint});
        for (auto message : validation.messages) {
            kernel::append_report_message(report, std::move(message));
        }
    }
    return report;
}

}
