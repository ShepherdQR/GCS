import gcs.constraint_catalog;
import gcs.kernel;

#include <gtest/gtest.h>

#include <cmath>

namespace {

namespace constraints = gcs::constraints;
namespace kernel = gcs::kernel;

kernel::ParameterVector point_parameters(double x, double y, double z) {
    kernel::ParameterVector parameters;
    parameters.dimension = kernel::geometry_dof(kernel::GeometryKind::point);
    parameters.values[0] = x;
    parameters.values[1] = y;
    parameters.values[2] = z;
    return parameters;
}

kernel::ParameterVector line_parameters(double x,
                                        double y,
                                        double z,
                                        double dx,
                                        double dy,
                                        double dz) {
    kernel::ParameterVector parameters;
    parameters.dimension = kernel::geometry_dof(kernel::GeometryKind::line);
    parameters.values[0] = x;
    parameters.values[1] = y;
    parameters.values[2] = z;
    parameters.values[3] = dx;
    parameters.values[4] = dy;
    parameters.values[5] = dz;
    return parameters;
}

kernel::ModelSnapshot make_distance_model(double second_x = 1.0, double distance = 1.0) {
    kernel::ModelDraft draft;
    draft.rigid_sets.push_back(kernel::RigidSetDraft{kernel::RigidSetId{1}, {kernel::EntityId{10}}});
    draft.rigid_sets.push_back(kernel::RigidSetDraft{kernel::RigidSetId{2}, {kernel::EntityId{11}}});
    draft.entities.push_back(kernel::EntityDraft{
        kernel::EntityId{10},
        kernel::GeometryKind::point,
        kernel::RigidSetId{1},
        point_parameters(0.0, 0.0, 0.0)});
    draft.entities.push_back(kernel::EntityDraft{
        kernel::EntityId{11},
        kernel::GeometryKind::point,
        kernel::RigidSetId{2},
        point_parameters(second_x, 0.0, 0.0)});
    draft.constraints.push_back(kernel::ConstraintDraft{
        kernel::ConstraintId{20},
        kernel::ConstraintKind::distance,
        {kernel::EntityId{10}, kernel::EntityId{11}},
        distance});
    return kernel::make_snapshot(draft).payload;
}

kernel::ModelSnapshot make_parallel_point_model() {
    auto model = make_distance_model();
    model.constraints.front().kind = kernel::ConstraintKind::parallel;
    model.constraints.front().value = 0.0;
    return model;
}

kernel::ModelSnapshot make_angle_model(double angle) {
    kernel::ModelDraft draft;
    draft.rigid_sets.push_back(kernel::RigidSetDraft{kernel::RigidSetId{1}, {kernel::EntityId{10}}});
    draft.rigid_sets.push_back(kernel::RigidSetDraft{kernel::RigidSetId{2}, {kernel::EntityId{11}}});
    draft.entities.push_back(kernel::EntityDraft{
        kernel::EntityId{10},
        kernel::GeometryKind::line,
        kernel::RigidSetId{1},
        line_parameters(0.0, 0.0, 0.0, 1.0, 0.0, 0.0)});
    draft.entities.push_back(kernel::EntityDraft{
        kernel::EntityId{11},
        kernel::GeometryKind::line,
        kernel::RigidSetId{2},
        line_parameters(0.0, 0.0, 0.0, 0.0, 1.0, 0.0)});
    draft.constraints.push_back(kernel::ConstraintDraft{
        kernel::ConstraintId{20},
        kernel::ConstraintKind::angle,
        {kernel::EntityId{10}, kernel::EntityId{11}},
        angle});
    return kernel::make_snapshot(draft).payload;
}

kernel::ModelSnapshot make_point_plane_distance_model() {
    kernel::ModelDraft draft;
    draft.rigid_sets.push_back(kernel::RigidSetDraft{kernel::RigidSetId{1}, {kernel::EntityId{10}}});
    draft.rigid_sets.push_back(kernel::RigidSetDraft{kernel::RigidSetId{2}, {kernel::EntityId{11}}});
    draft.entities.push_back(kernel::EntityDraft{
        kernel::EntityId{10},
        kernel::GeometryKind::point,
        kernel::RigidSetId{1},
        point_parameters(0.0, 0.0, 3.0)});
    draft.entities.push_back(kernel::EntityDraft{
        kernel::EntityId{11},
        kernel::GeometryKind::plane,
        kernel::RigidSetId{2},
        line_parameters(0.0, 0.0, 1.0, 0.0, 0.0, 1.0)});
    draft.constraints.push_back(kernel::ConstraintDraft{
        kernel::ConstraintId{20},
        kernel::ConstraintKind::distance,
        {kernel::EntityId{10}, kernel::EntityId{11}},
        2.0});
    return kernel::make_snapshot(draft).payload;
}

bool has_code(const kernel::StageReport& report, const char* code) {
    for (const auto& message : report.messages) {
        if (message.code.value == code) return true;
    }
    return false;
}

}  // namespace

TEST(ConstraintCatalogContract, DeclaresEveryBuiltinConstraintWithSchema) {
    const auto& catalog = constraints::builtin_catalog();

    EXPECT_EQ(catalog.version, "builtin-0.1");
    ASSERT_EQ(catalog.definitions.size(), 5U);
    for (const auto& definition : catalog.definitions) {
        EXPECT_FALSE(definition.name.empty());
        EXPECT_EQ(definition.catalog_version, catalog.version);
        EXPECT_EQ(definition.entity_signature.size(), 2U);
        EXPECT_GT(definition.residual_dimension, 0);
        EXPECT_GT(definition.generic_dof_effect, 0);
    }
}

TEST(ConstraintCatalogContract, RejectsInvalidArityWithStableReportCode) {
    auto model = make_distance_model();
    model.constraints.front().entity_ids.pop_back();

    auto validation = constraints::validate_constraint(
        constraints::builtin_catalog(),
        model,
        kernel::ConstraintId{20});

    EXPECT_FALSE(validation.payload.valid);
    EXPECT_EQ(validation.report.status, kernel::StageStatus::error);
    EXPECT_TRUE(has_code(validation.report, "constraint.invalid_arity"));
}

TEST(ConstraintCatalogContract, RejectsInvalidEntitySignature) {
    auto model = make_parallel_point_model();

    auto validation = constraints::validate_constraint(
        constraints::builtin_catalog(),
        model,
        kernel::ConstraintId{20});

    EXPECT_FALSE(validation.payload.valid);
    EXPECT_TRUE(has_code(validation.report, "constraint.invalid_entity_signature"));
}

TEST(ConstraintCatalogContract, RejectsInvalidScalarParameterSchema) {
    auto model = make_angle_model(4.0);

    auto validation = constraints::validate_constraint(
        constraints::builtin_catalog(),
        model,
        kernel::ConstraintId{20});

    EXPECT_FALSE(validation.payload.valid);
    EXPECT_TRUE(has_code(validation.report, "constraint.invalid_parameter_value"));
}

TEST(ConstraintCatalogContract, DistanceResidualDimensionMatchesCatalog) {
    auto model = make_distance_model(1.0, 1.0);

    auto residual = constraints::evaluate_residual(
        constraints::builtin_catalog(),
        constraints::ResidualEvaluationRequest{model, kernel::ConstraintId{20}});

    ASSERT_TRUE(residual.payload.valid);
    ASSERT_EQ(residual.payload.residuals.size(), 1U);
    EXPECT_EQ(residual.payload.definition.residual_dimension, 1);
    EXPECT_NEAR(residual.payload.residuals.front(), 0.0, 1.0e-12);
}

TEST(ConstraintCatalogContract, DistanceSupportsPointPlaneMetricSignature) {
    auto model = make_point_plane_distance_model();

    auto residual = constraints::evaluate_residual(
        constraints::builtin_catalog(),
        constraints::ResidualEvaluationRequest{model, kernel::ConstraintId{20}});

    ASSERT_TRUE(residual.payload.valid);
    ASSERT_EQ(residual.payload.residuals.size(), 1U);
    EXPECT_NEAR(residual.payload.residuals.front(), 0.0, 1.0e-12);
}

TEST(ConstraintCatalogContract, FiniteDifferenceJacobianCheckPassesForDistance) {
    auto model = make_distance_model(2.0, 1.5);

    auto check = constraints::check_jacobian(
        constraints::builtin_catalog(),
        constraints::FiniteDifferenceCheckRequest{
            model,
            kernel::ConstraintId{20},
            1.0e-6,
            1.0e-9});

    ASSERT_TRUE(check.payload.valid);
    EXPECT_TRUE(check.payload.passed);
    EXPECT_EQ(check.payload.analytic_jacobian.row_count, 1);
    EXPECT_EQ(check.payload.analytic_jacobian.column_count, 6);
    EXPECT_LE(check.payload.max_abs_error, 1.0e-9);
}

TEST(ConstraintCatalogContract, DegenerateDistanceReportsZeroDirection) {
    auto model = make_distance_model(0.0, 0.0);

    auto residual = constraints::evaluate_residual(
        constraints::builtin_catalog(),
        constraints::ResidualEvaluationRequest{model, kernel::ConstraintId{20}});

    ASSERT_TRUE(residual.payload.valid);
    EXPECT_TRUE(residual.payload.degeneracy_report.degenerate);
    EXPECT_EQ(residual.payload.degeneracy_report.code,
              "constraint.degenerate_zero_distance_direction");
    EXPECT_TRUE(has_code(residual.report, "constraint.degenerate_zero_distance_direction"));
}
