import gcs.contract_tools;
import gcs.decomposition_planner;
import gcs.incidence_graph;
import gcs.kernel;

#include <gtest/gtest.h>

namespace {

namespace graph = gcs::graph;
namespace kernel = gcs::kernel;
namespace planning = gcs::planning;

planning::PlannerOutput plan_for(const kernel::ModelSnapshot& model) {
    auto incidence = graph::build_incidence_indices(graph::IncidenceInput{model});
    return planning::plan_decomposition(
        planning::PlannerInput{model, incidence, model.solve_intent, {}});
}

bool has_code(const kernel::StageReport& report, const char* code) {
    for (const auto& message : report.messages) {
        if (message.code.value == code) return true;
    }
    return false;
}

}  // namespace

TEST(DecompositionPlannerContract, ComponentCoverHasRootAndBoundaryProjections) {
    auto model = gcs::tools::make_two_component_distance_model();

    auto plan = plan_for(model);

    EXPECT_EQ(plan.structural_report.status, kernel::StageStatus::ok);
    ASSERT_EQ(plan.cover_plan.contexts.size(), 3U);
    EXPECT_EQ(plan.cover_plan.root_context_id.value, 0U);
    ASSERT_EQ(plan.boundary_projections.size(), 2U);
    EXPECT_EQ(plan.cover_plan.boundary_projections.size(), plan.boundary_projections.size());
    EXPECT_EQ(plan.boundary_projections[0].source_context_id.value, 1U);
    EXPECT_EQ(plan.boundary_projections[0].target_context_id.value, 0U);
    EXPECT_EQ(plan.boundary_projections[1].source_context_id.value, 2U);
    EXPECT_EQ(plan.boundary_projections[1].target_context_id.value, 0U);
}

TEST(DecompositionPlannerContract, CoverValidationProvesModelCoverage) {
    auto model = gcs::tools::make_two_component_distance_model();
    auto plan = plan_for(model);

    auto validation = planning::validate_cover(model, plan.cover_plan);

    EXPECT_TRUE(validation.payload.valid);
    EXPECT_TRUE(validation.payload.covers_all_entities);
    EXPECT_TRUE(validation.payload.covers_all_constraints);
    EXPECT_TRUE(validation.payload.contexts_reference_known_ids);
    EXPECT_EQ(validation.payload.context_count, 3);
    EXPECT_EQ(validation.payload.boundary_projection_count, 2);
}

TEST(DecompositionPlannerContract, CoverValidationRejectsMissingEntityCoverage) {
    auto model = gcs::tools::make_two_component_distance_model();
    auto plan = plan_for(model);
    for (auto& context : plan.cover_plan.contexts) {
        context.entity_ids.clear();
    }

    auto validation = planning::validate_cover(model, plan.cover_plan);

    EXPECT_FALSE(validation.payload.valid);
    EXPECT_FALSE(validation.payload.covers_all_entities);
    EXPECT_TRUE(has_code(validation.report, "planner.cover_missing_entity"));
}

TEST(DecompositionPlannerContract, CoverValidationRejectsUnknownProjectionContext) {
    auto model = gcs::tools::make_two_component_distance_model();
    auto plan = plan_for(model);
    ASSERT_FALSE(plan.cover_plan.boundary_projections.empty());
    plan.cover_plan.boundary_projections.front().target_context_id = kernel::ContextId{999};

    auto validation = planning::validate_cover(model, plan.cover_plan);

    EXPECT_FALSE(validation.payload.valid);
    EXPECT_FALSE(validation.payload.boundary_projections_reference_known_contexts);
    EXPECT_TRUE(has_code(validation.report, "planner.cover_projection_missing_context"));
}

TEST(DecompositionPlannerContract, SolveOrderValidationAcceptsDeterministicPlan) {
    auto model = gcs::tools::make_two_component_distance_model();
    auto plan = plan_for(model);

    auto validation = planning::validate_solve_order(plan);

    EXPECT_TRUE(validation.payload.valid);
    EXPECT_TRUE(validation.payload.strictly_ordered);
    EXPECT_TRUE(validation.payload.every_step_has_context);
    EXPECT_TRUE(validation.payload.covers_all_subproblems);
    EXPECT_EQ(validation.payload.step_count, 2);
}

TEST(DecompositionPlannerContract, SolveOrderValidationRejectsSkippedOrder) {
    auto model = gcs::tools::make_two_component_distance_model();
    auto plan = plan_for(model);
    ASSERT_EQ(plan.solve_order.size(), 2U);
    plan.solve_order.back().order = 7;

    auto validation = planning::validate_solve_order(plan);

    EXPECT_FALSE(validation.payload.valid);
    EXPECT_FALSE(validation.payload.strictly_ordered);
    EXPECT_TRUE(has_code(validation.report, "planner.solve_order_not_strict"));
}

TEST(DecompositionPlannerContract, PlannerOutputIsDeterministic) {
    auto model = gcs::tools::make_two_component_distance_model();

    auto first = plan_for(model);
    auto second = plan_for(model);

    ASSERT_EQ(first.cover_plan.contexts.size(), second.cover_plan.contexts.size());
    ASSERT_EQ(first.boundary_projections.size(), second.boundary_projections.size());
    EXPECT_EQ(first.cover_plan.contexts[1].id.value, second.cover_plan.contexts[1].id.value);
    EXPECT_EQ(first.boundary_projections[0].id.value, second.boundary_projections[0].id.value);
    EXPECT_EQ(first.solve_order[0].context_id.value, second.solve_order[0].context_id.value);
    EXPECT_FALSE(first.unsupported_report.unsupported);
}
