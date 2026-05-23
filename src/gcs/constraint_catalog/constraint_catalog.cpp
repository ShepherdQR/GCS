module;

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <string>
#include <utility>
#include <vector>

module gcs.constraint_catalog;

import gcs.kernel;

namespace gcs::constraints {

namespace kernel = gcs::kernel;

namespace {

constexpr double pi = 3.14159265358979323846;

struct Vec3 {
    double x = 0.0;
    double y = 0.0;
    double z = 0.0;
};

kernel::StableId constraint_subject(ConstraintId id) {
    return kernel::StableId{"constraint", id.value};
}

kernel::StableId entity_subject(EntityId id) {
    return kernel::StableId{"entity", id.value};
}

ReportMessage make_message(kernel::ReportSeverity severity,
                           std::string code,
                           std::string summary,
                           std::vector<kernel::StableId> subjects) {
    return kernel::make_report_message(
        severity,
        kernel::ReportCode{std::move(code)},
        std::move(summary),
        std::move(subjects));
}

ReportMessage make_constraint_message(kernel::ReportSeverity severity,
                                      std::string code,
                                      std::string summary,
                                      ConstraintId constraint_id) {
    return make_message(
        severity,
        std::move(code),
        std::move(summary),
        {constraint_subject(constraint_id)});
}

EntitySignatureTerm point_term(std::string role) {
    return EntitySignatureTerm{std::move(role), {GeometryKind::point}, false};
}

EntitySignatureTerm oriented_term(std::string role) {
    return EntitySignatureTerm{
        std::move(role),
        {GeometryKind::line, GeometryKind::plane},
        true};
}

EntitySignatureTerm metric_term(std::string role) {
    return EntitySignatureTerm{
        std::move(role),
        {GeometryKind::point, GeometryKind::line, GeometryKind::plane},
        false};
}

ConstraintParameterSchema no_parameter() {
    return ConstraintParameterSchema{};
}

ConstraintParameterSchema length_parameter() {
    ConstraintParameterSchema schema;
    schema.kind = ConstraintParameterKind::length;
    schema.scalar_required = true;
    schema.min_value = 0.0;
    return schema;
}

ConstraintParameterSchema angle_parameter() {
    ConstraintParameterSchema schema;
    schema.kind = ConstraintParameterKind::angle_radians;
    schema.scalar_required = true;
    schema.min_value = 0.0;
    schema.max_value = pi;
    return schema;
}

bool has_kind(const std::vector<GeometryKind>& kinds, GeometryKind kind) {
    return std::find(kinds.begin(), kinds.end(), kind) != kinds.end();
}

bool scalar_parameter_is_valid(const ConstraintParameterSchema& schema, double value) {
    if (!schema.scalar_required) return true;
    if (value < schema.min_value) return false;
    if (schema.max_value > schema.min_value && value > schema.max_value) return false;
    return true;
}

Vec3 position_of(const kernel::EntityDraft& entity) {
    return Vec3{
        entity.parameters.values[0],
        entity.parameters.values[1],
        entity.parameters.values[2]};
}

Vec3 direction_of(const kernel::EntityDraft& entity) {
    return Vec3{
        entity.parameters.values[3],
        entity.parameters.values[4],
        entity.parameters.values[5]};
}

Vec3 subtract(Vec3 lhs, Vec3 rhs) {
    return Vec3{lhs.x - rhs.x, lhs.y - rhs.y, lhs.z - rhs.z};
}

double dot(Vec3 lhs, Vec3 rhs) {
    return lhs.x * rhs.x + lhs.y * rhs.y + lhs.z * rhs.z;
}

Vec3 cross(Vec3 lhs, Vec3 rhs) {
    return Vec3{
        lhs.y * rhs.z - lhs.z * rhs.y,
        lhs.z * rhs.x - lhs.x * rhs.z,
        lhs.x * rhs.y - lhs.y * rhs.x};
}

double norm(Vec3 value) {
    return std::sqrt(dot(value, value));
}

Vec3 normalized(Vec3 value) {
    const double length = norm(value);
    if (length <= 0.0) return Vec3{};
    return Vec3{value.x / length, value.y / length, value.z / length};
}

double clamped_dot(Vec3 lhs, Vec3 rhs) {
    return std::clamp(dot(lhs, rhs), -1.0, 1.0);
}

const ConstraintDraft* find_constraint_or_report(const ModelSnapshot& snapshot,
                                                 ConstraintId constraint_id,
                                                 StageReport& report) {
    const auto* constraint = kernel::find_constraint(snapshot, constraint_id);
    if (constraint == nullptr) {
        kernel::append_report_message(
            report,
            make_message(
                kernel::ReportSeverity::error,
                "constraint.missing_constraint",
                "Constraint ID is not present in the model snapshot.",
                {constraint_subject(constraint_id)}));
    }
    return constraint;
}

ConstraintValidationReport validate_constraint_against_catalog(
    const ConstraintCatalog& catalog,
    const ModelSnapshot& model,
    const ConstraintDraft& constraint) {
    ConstraintValidationReport result;
    const auto* definition = find_definition(catalog, constraint.kind);
    if (definition == nullptr) {
        result.messages.push_back(make_constraint_message(
            kernel::ReportSeverity::error,
            "constraint.unsupported_kind",
            "Constraint kind is not registered in the constraint catalog.",
            constraint.id));
        return result;
    }

    result.definition = *definition;
    result.valid = true;

    const auto entity_count = static_cast<int>(constraint.entity_ids.size());
    if (entity_count < definition->min_entity_count ||
        entity_count > definition->max_entity_count) {
        result.valid = false;
        result.messages.push_back(make_constraint_message(
            kernel::ReportSeverity::error,
            "constraint.invalid_arity",
            "Constraint entity count does not match its catalog signature.",
            constraint.id));
    }

    if (!scalar_parameter_is_valid(definition->parameter_schema, constraint.value)) {
        result.valid = false;
        result.messages.push_back(make_constraint_message(
            kernel::ReportSeverity::error,
            "constraint.invalid_parameter_value",
            "Constraint scalar parameter is outside its schema range.",
            constraint.id));
    }

    std::vector<kernel::RigidSetId> referenced_rigid_sets;
    for (std::size_t index = 0; index < constraint.entity_ids.size(); ++index) {
        EntityId entity_id = constraint.entity_ids[index];
        const auto* entity = kernel::find_entity(model, entity_id);
        if (entity == nullptr) {
            result.valid = false;
            auto message = make_constraint_message(
                kernel::ReportSeverity::error,
                "constraint.missing_entity",
                "Constraint references an entity that is not present in the model.",
                constraint.id);
            message.subjects.push_back(entity_subject(entity_id));
            result.messages.push_back(std::move(message));
            continue;
        }

        if (index < definition->entity_signature.size()) {
            const auto& term = definition->entity_signature[index];
            if (!has_kind(term.allowed_kinds, entity->kind)) {
                result.valid = false;
                auto message = make_constraint_message(
                    kernel::ReportSeverity::error,
                    "constraint.invalid_entity_signature",
                    "Constraint entity kind does not match its catalog signature.",
                    constraint.id);
                message.subjects.push_back(entity_subject(entity_id));
                result.messages.push_back(std::move(message));
            }

            if (term.requires_nonzero_direction &&
                norm(direction_of(*entity)) <= model.tolerances.residual) {
                result.valid = false;
                auto message = make_constraint_message(
                    kernel::ReportSeverity::error,
                    "constraint.degenerate_direction",
                    "Constraint requires a non-zero line direction or plane normal.",
                    constraint.id);
                message.subjects.push_back(entity_subject(entity_id));
                result.messages.push_back(std::move(message));
            }
        }

        if (definition->requires_distinct_rigid_sets &&
            kernel::contains_rigid_set(referenced_rigid_sets, entity->rigid_set_id)) {
            result.valid = false;
            auto message = make_constraint_message(
                kernel::ReportSeverity::error,
                "constraint.same_rigid_set",
                "Constraint endpoints must belong to distinct rigid sets.",
                constraint.id);
            message.subjects.push_back(entity_subject(entity_id));
            result.messages.push_back(std::move(message));
        }
        referenced_rigid_sets.push_back(entity->rigid_set_id);
    }

    return result;
}

DegeneracyReport make_non_degenerate_report(ConstraintId constraint_id) {
    DegeneracyReport report;
    report.constraint_ids.push_back(constraint_id);
    return report;
}

DegeneracyReport probe_degeneracy_for_constraint(const ModelSnapshot& model,
                                                 const ConstraintDraft& constraint,
                                                 const ConstraintDefinition& definition) {
    DegeneracyReport report = make_non_degenerate_report(constraint.id);
    for (EntityId entity_id : constraint.entity_ids) {
        report.entity_ids.push_back(entity_id);
    }

    if (constraint.entity_ids.size() < 2) return report;
    const auto* first = kernel::find_entity(model, constraint.entity_ids[0]);
    const auto* second = kernel::find_entity(model, constraint.entity_ids[1]);
    if (first == nullptr || second == nullptr) return report;

    if (definition.kind == ConstraintKind::distance) {
        if ((first->kind == GeometryKind::line || first->kind == GeometryKind::plane) &&
            norm(direction_of(*first)) <= model.tolerances.residual) {
            report.degenerate = true;
            report.code = "constraint.degenerate_direction";
            report.message =
                "Distance constraint references a line direction or plane normal with zero length.";
            return report;
        }
        if ((second->kind == GeometryKind::line || second->kind == GeometryKind::plane) &&
            norm(direction_of(*second)) <= model.tolerances.residual) {
            report.degenerate = true;
            report.code = "constraint.degenerate_direction";
            report.message =
                "Distance constraint references a line direction or plane normal with zero length.";
            return report;
        }

        const bool point_point = first->kind == GeometryKind::point &&
                                 second->kind == GeometryKind::point;
        const double separation = norm(subtract(position_of(*first), position_of(*second)));
        if (point_point && separation <= model.tolerances.residual) {
            report.degenerate = true;
            report.code = "constraint.degenerate_zero_distance_direction";
            report.message =
                "Distance residual is evaluable, but its direction derivative is undefined at zero separation.";
        }
        return report;
    }

    for (std::size_t i = 0; i < constraint.entity_ids.size() &&
                            i < definition.entity_signature.size();
         ++i) {
        const auto* entity = kernel::find_entity(model, constraint.entity_ids[i]);
        if (entity != nullptr &&
            definition.entity_signature[i].requires_nonzero_direction &&
            norm(direction_of(*entity)) <= model.tolerances.residual) {
            report.degenerate = true;
            report.code = "constraint.degenerate_direction";
            report.message =
                "Constraint requires a non-zero line direction or plane normal.";
            return report;
        }
    }

    return report;
}

bool evaluate_residual_values(const ModelSnapshot& model,
                              const ConstraintDraft& constraint,
                              const ConstraintDefinition& definition,
                              std::vector<double>& residuals) {
    if (constraint.entity_ids.size() < 2) return false;
    const auto* first = kernel::find_entity(model, constraint.entity_ids[0]);
    const auto* second = kernel::find_entity(model, constraint.entity_ids[1]);
    if (first == nullptr || second == nullptr) return false;

    residuals.clear();
    switch (definition.kind) {
        case ConstraintKind::coincident: {
            const Vec3 delta = subtract(position_of(*first), position_of(*second));
            residuals = {delta.x, delta.y, delta.z};
            return true;
        }
        case ConstraintKind::distance: {
            double distance = 0.0;
            if (first->kind == GeometryKind::point && second->kind == GeometryKind::point) {
                distance = norm(subtract(position_of(*first), position_of(*second)));
            } else if (first->kind == GeometryKind::point &&
                       second->kind == GeometryKind::plane) {
                const Vec3 normal = normalized(direction_of(*second));
                distance = dot(subtract(position_of(*first), position_of(*second)), normal);
            } else if (first->kind == GeometryKind::plane &&
                       second->kind == GeometryKind::point) {
                const Vec3 normal = normalized(direction_of(*first));
                distance = dot(subtract(position_of(*second), position_of(*first)), normal);
            } else if (first->kind == GeometryKind::point &&
                       second->kind == GeometryKind::line) {
                const Vec3 direction = normalized(direction_of(*second));
                distance = norm(cross(subtract(position_of(*first), position_of(*second)), direction));
            } else if (first->kind == GeometryKind::line &&
                       second->kind == GeometryKind::point) {
                const Vec3 direction = normalized(direction_of(*first));
                distance = norm(cross(subtract(position_of(*second), position_of(*first)), direction));
            } else {
                return false;
            }
            residuals = {distance - constraint.value};
            return true;
        }
        case ConstraintKind::parallel: {
            const Vec3 lhs = normalized(direction_of(*first));
            const Vec3 rhs = normalized(direction_of(*second));
            const Vec3 residual = cross(lhs, rhs);
            residuals = {residual.x, residual.y};
            return true;
        }
        case ConstraintKind::perpendicular: {
            const Vec3 lhs = normalized(direction_of(*first));
            const Vec3 rhs = normalized(direction_of(*second));
            residuals = {dot(lhs, rhs)};
            return true;
        }
        case ConstraintKind::angle: {
            const Vec3 lhs = normalized(direction_of(*first));
            const Vec3 rhs = normalized(direction_of(*second));
            residuals = {std::acos(clamped_dot(lhs, rhs)) - constraint.value};
            return true;
        }
    }
    return false;
}

bool set_entity_parameter(ModelSnapshot& model,
                          EntityId entity_id,
                          int parameter_index,
                          double value) {
    for (auto& entity : model.entities) {
        if (entity.id == entity_id) {
            entity.parameters.values[static_cast<std::size_t>(parameter_index)] = value;
            return true;
        }
    }
    return false;
}

double entity_parameter_value(const ModelSnapshot& model,
                              EntityId entity_id,
                              int parameter_index) {
    const auto* entity = kernel::find_entity(model, entity_id);
    if (entity == nullptr) return 0.0;
    return entity->parameters.values[static_cast<std::size_t>(parameter_index)];
}

gcs::kernel::ContractResult<JacobianEvaluationResult> finite_difference_jacobian(
    const ConstraintCatalog& catalog,
    JacobianEvaluationRequest request) {
    kernel::ContractResult<JacobianEvaluationResult> result;
    result.report = kernel::make_stage_report("constraint_catalog.evaluate_jacobian");

    if (request.finite_difference_step <= 0.0) {
        kernel::append_report_message(
            result.report,
            make_message(
                kernel::ReportSeverity::error,
                "constraint.invalid_finite_difference_step",
                "Finite-difference step must be positive.",
                {constraint_subject(request.constraint_id)}));
        return result;
    }

    auto base_residual = evaluate_residual(
        catalog,
        ResidualEvaluationRequest{request.model, request.constraint_id});
    for (auto message : base_residual.report.messages) {
        kernel::append_report_message(result.report, std::move(message));
    }
    if (!base_residual.payload.valid) return result;

    const auto* constraint = kernel::find_constraint(request.model, request.constraint_id);
    if (constraint == nullptr) return result;

    result.payload.definition = base_residual.payload.definition;
    result.payload.row_count = static_cast<int>(base_residual.payload.residuals.size());
    result.payload.degeneracy_report = base_residual.payload.degeneracy_report;

    for (EntityId entity_id : constraint->entity_ids) {
        const auto* entity = kernel::find_entity(request.model, entity_id);
        if (entity == nullptr) continue;
        result.payload.entity_ids.push_back(entity_id);
        result.payload.entity_parameter_dimensions.push_back(entity->parameters.dimension);
        result.payload.column_count += entity->parameters.dimension;
    }

    result.payload.values.assign(
        static_cast<std::size_t>(result.payload.row_count * result.payload.column_count),
        0.0);

    int column_offset = 0;
    for (EntityId entity_id : result.payload.entity_ids) {
        const auto* entity = kernel::find_entity(request.model, entity_id);
        if (entity == nullptr) continue;

        for (int parameter_index = 0; parameter_index < entity->parameters.dimension;
             ++parameter_index) {
            const double original = entity_parameter_value(
                request.model,
                entity_id,
                parameter_index);

            ModelSnapshot plus = request.model;
            ModelSnapshot minus = request.model;
            set_entity_parameter(
                plus,
                entity_id,
                parameter_index,
                original + request.finite_difference_step);
            set_entity_parameter(
                minus,
                entity_id,
                parameter_index,
                original - request.finite_difference_step);

            auto plus_residual = evaluate_residual(
                catalog,
                ResidualEvaluationRequest{plus, request.constraint_id});
            auto minus_residual = evaluate_residual(
                catalog,
                ResidualEvaluationRequest{minus, request.constraint_id});
            if (!plus_residual.payload.valid || !minus_residual.payload.valid) {
                kernel::append_report_message(
                    result.report,
                    make_message(
                        kernel::ReportSeverity::error,
                        "constraint.finite_difference_failed",
                        "Residual evaluation failed during finite-difference Jacobian assembly.",
                        {constraint_subject(request.constraint_id),
                         entity_subject(entity_id)}));
                return result;
            }

            for (int row = 0; row < result.payload.row_count; ++row) {
                const double derivative =
                    (plus_residual.payload.residuals[static_cast<std::size_t>(row)] -
                     minus_residual.payload.residuals[static_cast<std::size_t>(row)]) /
                    (2.0 * request.finite_difference_step);
                const auto offset = static_cast<std::size_t>(
                    row * result.payload.column_count + column_offset + parameter_index);
                result.payload.values[offset] = derivative;
            }
        }

        column_offset += entity->parameters.dimension;
    }

    result.payload.valid = true;
    return result;
}

}  // namespace

const ConstraintCatalog& builtin_catalog() {
    static const ConstraintCatalog catalog = [] {
        ConstraintCatalog value;
        value.version = "builtin-0.1";
        value.definitions = {
            ConstraintDefinition{
                ConstraintKind::coincident,
                "Coincident",
                value.version,
                2,
                2,
                3,
                3,
                true,
                no_parameter(),
                {point_term("first"), point_term("second")},
                ConstraintEvaluatorPolicy::finite_difference_baseline,
                {}},
            ConstraintDefinition{
                ConstraintKind::parallel,
                "Parallel",
                value.version,
                2,
                2,
                2,
                2,
                true,
                no_parameter(),
                {oriented_term("first"), oriented_term("second")},
                ConstraintEvaluatorPolicy::finite_difference_baseline,
                {"constraint.degenerate_direction"}},
            ConstraintDefinition{
                ConstraintKind::perpendicular,
                "Perpendicular",
                value.version,
                2,
                2,
                1,
                1,
                true,
                no_parameter(),
                {oriented_term("first"), oriented_term("second")},
                ConstraintEvaluatorPolicy::finite_difference_baseline,
                {"constraint.degenerate_direction"}},
            ConstraintDefinition{
                ConstraintKind::distance,
                "Distance",
                value.version,
                2,
                2,
                1,
                1,
                true,
                length_parameter(),
                {metric_term("first"), metric_term("second")},
                ConstraintEvaluatorPolicy::finite_difference_baseline,
                {"constraint.degenerate_zero_distance_direction",
                 "constraint.degenerate_direction"}},
            ConstraintDefinition{
                ConstraintKind::angle,
                "Angle",
                value.version,
                2,
                2,
                1,
                1,
                true,
                angle_parameter(),
                {oriented_term("first"), oriented_term("second")},
                ConstraintEvaluatorPolicy::finite_difference_baseline,
                {"constraint.degenerate_direction"}},
        };
        return value;
    }();
    return catalog;
}

const std::vector<ConstraintDefinition>& builtin_definitions() {
    return builtin_catalog().definitions;
}

const ConstraintDefinition* find_definition(const ConstraintCatalog& catalog,
                                            ConstraintKind kind) {
    for (const auto& definition : catalog.definitions) {
        if (definition.kind == kind) return &definition;
    }
    return nullptr;
}

const ConstraintDefinition* find_definition(ConstraintKind kind) {
    return find_definition(builtin_catalog(), kind);
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
    return validate_constraint_against_catalog(
        builtin_catalog(),
        input.model,
        input.constraint);
}

gcs::kernel::ContractResult<ConstraintValidationReport> validate_constraint(
    const ConstraintCatalog& catalog,
    const ModelSnapshot& snapshot,
    ConstraintId constraint_id) {
    kernel::ContractResult<ConstraintValidationReport> result;
    result.report = kernel::make_stage_report("constraint_catalog.validate_constraint");

    const auto* constraint = find_constraint_or_report(snapshot, constraint_id, result.report);
    if (constraint == nullptr) return result;

    result.payload = validate_constraint_against_catalog(catalog, snapshot, *constraint);
    for (auto message : result.payload.messages) {
        kernel::append_report_message(result.report, std::move(message));
    }
    return result;
}

StageReport validate_model_constraints(const ModelSnapshot& model) {
    StageReport report = kernel::make_stage_report("constraint_catalog.validate_model");
    for (const auto& constraint : model.constraints) {
        auto validation = validate_constraint_against_catalog(
            builtin_catalog(),
            model,
            constraint);
        for (auto message : validation.messages) {
            kernel::append_report_message(report, std::move(message));
        }
    }
    return report;
}

gcs::kernel::ContractResult<DegeneracyReport> probe_degeneracy(
    const ConstraintCatalog& catalog,
    DegeneracyProbeRequest request) {
    kernel::ContractResult<DegeneracyReport> result;
    result.report = kernel::make_stage_report("constraint_catalog.probe_degeneracy");

    const auto* constraint = find_constraint_or_report(
        request.model,
        request.constraint_id,
        result.report);
    if (constraint == nullptr) return result;

    auto validation = validate_constraint_against_catalog(catalog, request.model, *constraint);
    for (auto message : validation.messages) {
        kernel::append_report_message(result.report, std::move(message));
    }
    result.payload = probe_degeneracy_for_constraint(
        request.model,
        *constraint,
        validation.definition);
    return result;
}

gcs::kernel::ContractResult<ResidualEvaluationResult> evaluate_residual(
    const ConstraintCatalog& catalog,
    ResidualEvaluationRequest request) {
    kernel::ContractResult<ResidualEvaluationResult> result;
    result.report = kernel::make_stage_report("constraint_catalog.evaluate_residual");

    const auto* constraint = find_constraint_or_report(
        request.model,
        request.constraint_id,
        result.report);
    if (constraint == nullptr) return result;

    auto validation = validate_constraint_against_catalog(catalog, request.model, *constraint);
    result.payload.definition = validation.definition;
    for (auto message : validation.messages) {
        kernel::append_report_message(result.report, std::move(message));
    }
    if (!validation.valid) return result;

    result.payload.degeneracy_report = probe_degeneracy_for_constraint(
        request.model,
        *constraint,
        validation.definition);
    if (result.payload.degeneracy_report.degenerate) {
        kernel::append_report_message(
            result.report,
            make_message(
                kernel::ReportSeverity::warning,
                result.payload.degeneracy_report.code,
                result.payload.degeneracy_report.message,
                {constraint_subject(constraint->id)}));
    }

    if (!evaluate_residual_values(
            request.model,
            *constraint,
            validation.definition,
            result.payload.residuals)) {
        kernel::append_report_message(
            result.report,
            make_constraint_message(
                kernel::ReportSeverity::error,
                "constraint.residual_evaluation_failed",
                "Constraint residual evaluator could not produce a residual vector.",
                constraint->id));
        return result;
    }

    if (static_cast<int>(result.payload.residuals.size()) !=
        validation.definition.residual_dimension) {
        kernel::append_report_message(
            result.report,
            make_constraint_message(
                kernel::ReportSeverity::error,
                "constraint.residual_shape_mismatch",
                "Residual vector size does not match the catalog definition.",
                constraint->id));
        return result;
    }

    result.payload.valid = true;
    return result;
}

gcs::kernel::ContractResult<JacobianEvaluationResult> evaluate_jacobian(
    const ConstraintCatalog& catalog,
    JacobianEvaluationRequest request) {
    return finite_difference_jacobian(catalog, std::move(request));
}

gcs::kernel::ContractResult<JacobianCheckReport> check_jacobian(
    const ConstraintCatalog& catalog,
    FiniteDifferenceCheckRequest request) {
    kernel::ContractResult<JacobianCheckReport> result;
    result.report = kernel::make_stage_report("constraint_catalog.check_jacobian");

    if (request.tolerance <= 0.0) {
        kernel::append_report_message(
            result.report,
            make_message(
                kernel::ReportSeverity::error,
                "constraint.invalid_jacobian_check_tolerance",
                "Jacobian check tolerance must be positive.",
                {constraint_subject(request.constraint_id)}));
        return result;
    }

    auto analytic = evaluate_jacobian(
        catalog,
        JacobianEvaluationRequest{
            request.model,
            request.constraint_id,
            request.finite_difference_step});
    auto finite_difference = finite_difference_jacobian(
        catalog,
        JacobianEvaluationRequest{
            request.model,
            request.constraint_id,
            request.finite_difference_step});

    for (auto message : analytic.report.messages) {
        kernel::append_report_message(result.report, std::move(message));
    }
    if (!analytic.payload.valid || !finite_difference.payload.valid) {
        result.payload.analytic_jacobian = std::move(analytic.payload);
        result.payload.finite_difference_jacobian = std::move(finite_difference.payload);
        return result;
    }

    result.payload.analytic_jacobian = std::move(analytic.payload);
    result.payload.finite_difference_jacobian = std::move(finite_difference.payload);
    result.payload.valid = true;

    const auto& lhs = result.payload.analytic_jacobian.values;
    const auto& rhs = result.payload.finite_difference_jacobian.values;
    const std::size_t count = lhs.size() < rhs.size() ? lhs.size() : rhs.size();
    for (std::size_t i = 0; i < count; ++i) {
        result.payload.max_abs_error = std::max(
            result.payload.max_abs_error,
            std::abs(lhs[i] - rhs[i]));
    }
    result.payload.passed = result.payload.max_abs_error <= request.tolerance &&
                            lhs.size() == rhs.size();
    if (!result.payload.passed) {
        kernel::append_report_message(
            result.report,
            make_message(
                kernel::ReportSeverity::error,
                "constraint.jacobian_check_failed",
                "Jacobian check exceeded tolerance.",
                {constraint_subject(request.constraint_id)}));
    }
    return result;
}

}
