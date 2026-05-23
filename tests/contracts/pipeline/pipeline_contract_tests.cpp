import gcs.constraint_catalog;
import gcs.contract_tools;
import gcs.decomposition_planner;
import gcs.incidence_graph;
import gcs.kernel;
import gcs.session_runtime;

#include <gtest/gtest.h>

namespace {

namespace kernel = gcs::kernel;

}  // namespace

TEST(PipelineContract, ConstraintCatalogAcceptsCanonicalDistanceConstraint) {
    auto model = gcs::tools::make_two_point_distance_model();
    const auto& constraint = model.constraints.front();

    auto result = gcs::constraints::validate_constraint(
        gcs::constraints::ConstraintValidationInput{model, constraint});

    EXPECT_TRUE(result.valid);
    EXPECT_EQ(result.definition.residual_dimension, 1);
    EXPECT_TRUE(result.messages.empty());
}

TEST(PipelineContract, IncidenceAndPlannerProduceCanonicalCover) {
    auto model = gcs::tools::make_two_point_distance_model();
    auto incidence = gcs::graph::build_incidence_indices(gcs::graph::IncidenceInput{model});
    auto plan = gcs::planning::plan_decomposition(
        gcs::planning::PlannerInput{model, incidence, model.solve_intent, {}});

    EXPECT_FALSE(plan.cover_plan.contexts.empty());
    EXPECT_FALSE(plan.subproblems.empty());
    EXPECT_EQ(plan.cover_plan.root_context_id.value, 0U);
    EXPECT_EQ(plan.cover_plan.contexts.front().state_version.value, model.state_version.value);
}

TEST(PipelineContract, RuntimeCommitsAcceptedCanonicalState) {
    auto model = gcs::tools::make_two_point_distance_model();
    gcs::runtime::SessionRuntime runtime(model);

    auto result = runtime.solve();

    EXPECT_TRUE(result.accepted);
    EXPECT_TRUE(result.gluing_report.accepted);
    EXPECT_FALSE(result.gluing_report.obstruction_report.present);
    EXPECT_EQ(result.user_visible_status, kernel::SolveStatus::accepted_with_warnings);
    EXPECT_EQ(result.pre_solve_diagnostics.status_code,
              kernel::SolveStatus::under_constrained);
    EXPECT_EQ(runtime.current_snapshot().state_version.value, 1U);
}
