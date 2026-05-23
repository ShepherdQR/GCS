import gcs.contract_tools;
import gcs.kernel;
import gcs.numeric_engine;

#include <gtest/gtest.h>

namespace {

namespace kernel = gcs::kernel;
namespace numeric = gcs::numeric;

numeric::NumericTask make_task() {
    auto model = gcs::tools::make_two_point_distance_model();
    auto context = gcs::tools::make_whole_context_for(model);
    return numeric::make_numeric_task(
        model,
        context,
        context.entity_ids,
        context.constraint_ids,
        kernel::GaugePolicy{});
}

bool has_code(const kernel::StageReport& report, const char* code) {
    for (const auto& message : report.messages) {
        if (message.code.value == code) return true;
    }
    return false;
}

}  // namespace

TEST(NumericEngineContract, ValidatesCanonicalTask) {
    auto task = make_task();

    auto validation = numeric::validate_task(task);

    EXPECT_TRUE(validation.payload.valid);
    EXPECT_TRUE(validation.payload.context_version_matches);
    EXPECT_TRUE(validation.payload.active_variables_exist);
    EXPECT_TRUE(validation.payload.active_equations_exist);
    EXPECT_TRUE(validation.payload.active_variables_within_context);
    EXPECT_TRUE(validation.payload.active_equations_within_context);
}

TEST(NumericEngineContract, RejectsMissingActiveEntity) {
    auto task = make_task();
    task.active_variables.push_back(kernel::EntityId{999});

    auto validation = numeric::validate_task(task);

    EXPECT_FALSE(validation.payload.valid);
    EXPECT_FALSE(validation.payload.active_variables_exist);
    EXPECT_TRUE(has_code(validation.report, "numeric.missing_entity"));
}

TEST(NumericEngineContract, RejectsMissingActiveConstraint) {
    auto task = make_task();
    task.active_equations.push_back(kernel::ConstraintId{999});

    auto validation = numeric::validate_task(task);

    EXPECT_FALSE(validation.payload.valid);
    EXPECT_FALSE(validation.payload.active_equations_exist);
    EXPECT_TRUE(has_code(validation.report, "numeric.missing_constraint"));
}

TEST(NumericEngineContract, RejectsBoundaryVariableOutsideActiveSet) {
    auto task = make_task();
    task.boundary_variables.push_back(kernel::EntityId{77});

    auto validation = numeric::validate_task(task);

    EXPECT_FALSE(validation.payload.valid);
    EXPECT_FALSE(validation.payload.boundary_variables_are_active);
    EXPECT_TRUE(has_code(validation.report, "numeric.boundary_not_active"));
}

TEST(NumericEngineContract, AssemblesResidualsThroughCatalog) {
    auto task = make_task();

    auto assembly = numeric::assemble_equations(task);

    ASSERT_TRUE(assembly.payload.valid);
    EXPECT_EQ(assembly.payload.variable_dimension, 6);
    EXPECT_EQ(assembly.payload.residual_dimension, 1);
    ASSERT_EQ(assembly.payload.residual_blocks.size(), 1U);
    EXPECT_EQ(assembly.payload.residual_blocks.front().constraint_id.value, 0U);
    ASSERT_EQ(assembly.payload.residual_vector.size(), 1U);
    EXPECT_NEAR(assembly.payload.residual_vector.front(), 0.0, 1.0e-12);
}

TEST(NumericEngineContract, SolveLocalConsumesAssemblyEvidence) {
    auto task = make_task();

    auto report = numeric::solve_local(task);

    EXPECT_EQ(report.result_code, kernel::SolveStatus::solved);
    EXPECT_TRUE(report.local_section.valid);
    EXPECT_EQ(report.local_section.entity_states.size(), task.active_variables.size());
    EXPECT_EQ(report.rank_estimate, 1);
    EXPECT_NEAR(report.initial_residual, 0.0, 1.0e-12);
    EXPECT_TRUE(has_code(report.stage_report, "numeric.local_section.placeholder"));
}
