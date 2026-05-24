import gcs.contract_tools;
import gcs.kernel;
import gcs.numeric_engine;

#include <gtest/gtest.h>

namespace {

namespace kernel = gcs::kernel;
namespace numeric = gcs::numeric;

numeric::NumericTask make_task_for_model(kernel::ModelSnapshot model) {
    auto context = gcs::tools::make_whole_context_for(model);
    return numeric::make_numeric_task(
        model,
        context,
        context.entity_ids,
        context.constraint_ids,
        kernel::GaugePolicy{});
}

numeric::NumericTask make_task() {
    return make_task_for_model(gcs::tools::make_two_point_distance_model());
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

TEST(NumericEngineContract, AssemblesJacobianInActiveVariableOrder) {
    auto task = make_task();

    auto assembly = numeric::assemble_equations(task);

    ASSERT_TRUE(assembly.payload.valid);
    EXPECT_TRUE(assembly.payload.jacobian_report.valid);
    EXPECT_EQ(assembly.payload.jacobian_report.row_count, 1);
    EXPECT_EQ(assembly.payload.jacobian_report.column_count, 6);
    ASSERT_EQ(assembly.payload.jacobian_report.blocks.size(), 1U);
    const auto& block = assembly.payload.jacobian_report.blocks.front();
    EXPECT_EQ(block.row_offset, 0);
    EXPECT_EQ(block.row_count, 1);
    EXPECT_EQ(block.column_count, 6);
    ASSERT_EQ(block.entity_column_offsets.size(), 2U);
    EXPECT_EQ(block.entity_column_offsets[0], 0);
    EXPECT_EQ(block.entity_column_offsets[1], 3);
    ASSERT_EQ(assembly.payload.jacobian_report.values.size(), 6U);
    EXPECT_NEAR(assembly.payload.jacobian_report.values[0], -1.0, 1.0e-6);
    EXPECT_NEAR(assembly.payload.jacobian_report.values[3], 1.0, 1.0e-6);
}

TEST(NumericEngineContract, SolveLocalConsumesAssemblyEvidence) {
    auto task = make_task();

    auto report = numeric::solve_local(task);

    EXPECT_EQ(report.result_code, kernel::SolveStatus::solved);
    EXPECT_TRUE(report.local_section.valid);
    EXPECT_EQ(report.local_section.entity_states.size(), task.active_variables.size());
    EXPECT_EQ(report.rank_estimate, 1);
    EXPECT_NEAR(report.initial_residual, 0.0, 1.0e-12);
    EXPECT_NEAR(report.final_residual, 0.0, 1.0e-12);
    EXPECT_TRUE(has_code(report.stage_report, "numeric.local_section.converged"));
}

TEST(NumericEngineContract, ReportsResidualMetricsForUnsatisfiedFixture) {
    auto task = make_task_for_model(gcs::tools::make_unsatisfied_two_point_distance_model());

    auto report = numeric::solve_local(task);

    EXPECT_EQ(report.result_code, kernel::SolveStatus::solved);
    EXPECT_EQ(report.residual_report.dimension, 1);
    EXPECT_NEAR(report.initial_residual, 1.0, 1.0e-12);
    EXPECT_LT(report.final_residual, report.initial_residual);
    EXPECT_LE(report.final_residual, task.tolerances.residual);
    EXPECT_NEAR(report.residual_report.norm, report.final_residual, 1.0e-12);
    EXPECT_NEAR(report.residual_report.max_abs_value, report.final_residual, 1.0e-12);
    EXPECT_GT(report.iteration_count, 0);
    EXPECT_GT(report.step_norm, 0.0);
    ASSERT_EQ(report.residual_report.blocks.size(), 1U);
    EXPECT_NEAR(report.residual_report.blocks.front().norm, report.final_residual, 1.0e-12);
}

TEST(NumericEngineContract, ConvergesWhenEachResidualIsWithinTolerance) {
    auto task = make_task_for_model(
        gcs::tools::make_tolerated_multi_residual_distance_model());
    task.solve_limits.max_iterations = 0;

    auto report = numeric::solve_local(task);

    EXPECT_EQ(report.result_code, kernel::SolveStatus::solved);
    EXPECT_TRUE(report.local_section.valid);
    EXPECT_GT(report.final_residual, task.tolerances.residual);
    EXPECT_LE(report.residual_report.max_abs_value, task.tolerances.residual);
    ASSERT_EQ(report.residual_report.blocks.size(), 2U);
    EXPECT_LE(report.residual_report.blocks[0].max_abs_value,
              task.tolerances.residual);
    EXPECT_LE(report.residual_report.blocks[1].max_abs_value,
              task.tolerances.residual);
    ASSERT_EQ(report.iteration_trace.entries.size(), 2U);
    EXPECT_EQ(report.iteration_trace.entries.back().phase, "converged");
}

TEST(NumericEngineContract, ReportsRankConditionEvidence) {
    auto task = make_task();

    auto report = numeric::solve_local(task);

    EXPECT_EQ(report.rank_condition_report.variable_dimension, 6);
    EXPECT_EQ(report.rank_condition_report.free_variable_dimension, 6);
    EXPECT_EQ(report.rank_condition_report.frozen_variable_dimension, 0);
    EXPECT_EQ(report.rank_condition_report.residual_dimension, 1);
    EXPECT_EQ(report.rank_condition_report.rank_estimate, 1);
    EXPECT_EQ(report.rank_condition_report.nullity_estimate, 5);
    EXPECT_TRUE(report.rank_condition_report.under_constrained);
    EXPECT_FALSE(report.rank_condition_report.over_constrained);
    EXPECT_TRUE(report.rank_condition_report.condition_estimate_available);
    EXPECT_NEAR(report.rank_condition_report.condition_estimate, 1.0, 1.0e-6);
}

TEST(NumericEngineContract, SingularRankDoesNotPublishFiniteConditionEstimate) {
    auto task = make_task_for_model(gcs::tools::make_redundant_distance_pair_model());

    auto report = numeric::solve_local(task);

    EXPECT_EQ(report.result_code, kernel::SolveStatus::solved);
    EXPECT_EQ(report.rank_condition_report.rank_estimate, 1);
    EXPECT_TRUE(report.rank_condition_report.numerically_singular);
    EXPECT_FALSE(report.rank_condition_report.condition_estimate_available);
    EXPECT_NEAR(report.rank_condition_report.condition_estimate, 0.0, 1.0e-12);
}

TEST(NumericEngineContract, RankEvidenceUsesOnlyFreeBoundaryColumns) {
    auto task = make_task();
    task.boundary_variables.push_back(kernel::EntityId{0});

    auto report = numeric::solve_local(task);

    EXPECT_EQ(report.rank_condition_report.variable_dimension, 6);
    EXPECT_EQ(report.rank_condition_report.free_variable_dimension, 3);
    EXPECT_EQ(report.rank_condition_report.frozen_variable_dimension, 3);
    EXPECT_EQ(report.rank_condition_report.rank_estimate, 1);
    EXPECT_EQ(report.rank_condition_report.nullity_estimate, 2);
    EXPECT_TRUE(report.rank_condition_report.under_constrained);
    EXPECT_FALSE(report.rank_condition_report.over_constrained);
}

TEST(NumericEngineContract, ReportsBoundaryVariablesWithoutMutation) {
    auto task = make_task();
    task.boundary_variables.push_back(kernel::EntityId{0});

    auto report = numeric::solve_local(task);

    ASSERT_EQ(report.boundary_variables.size(), 1U);
    EXPECT_TRUE(report.boundary_variables.front().active);
    EXPECT_TRUE(report.boundary_variables.front().unchanged);
    EXPECT_EQ(report.boundary_variables.front().before.dimension, 3);
    EXPECT_EQ(report.boundary_variables.front().after.dimension, 3);
}

TEST(NumericEngineContract, TraceIsReplayableForIterativeSolve) {
    auto task = make_task();

    auto report = numeric::solve_local(task);

    EXPECT_EQ(report.iteration_trace.base_version.value, task.problem_snapshot.state_version.value);
    ASSERT_EQ(report.iteration_trace.entries.size(), 2U);
    EXPECT_EQ(report.iteration_trace.entries.front().phase, "initial");
    EXPECT_FALSE(report.iteration_trace.entries.front().accepted);
    EXPECT_EQ(report.iteration_trace.entries.back().phase, "converged");
    EXPECT_TRUE(report.iteration_trace.entries.back().accepted);
    EXPECT_NEAR(report.iteration_trace.entries.back().residual_norm,
                report.final_residual,
                1.0e-12);
    EXPECT_NEAR(report.iteration_trace.entries.back().step_norm, 0.0, 1.0e-12);
}

TEST(NumericEngineContract, TraceRecordsAcceptedDampedSteps) {
    auto task = make_task_for_model(gcs::tools::make_unsatisfied_two_point_distance_model());

    auto report = numeric::solve_local(task);

    ASSERT_GE(report.iteration_trace.entries.size(), 3U);
    EXPECT_EQ(report.iteration_trace.entries[1].phase, "damped_gauss_newton");
    EXPECT_TRUE(report.iteration_trace.entries[1].accepted);
    EXPECT_LT(report.iteration_trace.entries[1].residual_norm,
              report.iteration_trace.entries.front().residual_norm);
    EXPECT_GT(report.iteration_trace.entries[1].step_norm, 0.0);
    EXPECT_EQ(report.iteration_trace.entries.back().phase, "converged");
}
