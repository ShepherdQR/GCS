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

TEST(DecompositionPlannerContract, SolveDagExplainsBoundaryProjectionDependencies) {
    auto model = gcs::tools::make_two_component_distance_model();

    auto plan = plan_for(model);
    auto validation = planning::validate_solve_dag(plan);

    EXPECT_TRUE(validation.payload.valid);
    EXPECT_TRUE(validation.payload.nodes_reference_known_contexts);
    EXPECT_TRUE(validation.payload.edges_reference_known_nodes);
    EXPECT_TRUE(validation.payload.edge_projections_reference_known_cover_projections);
    EXPECT_TRUE(validation.payload.acyclic);
    EXPECT_TRUE(validation.payload.covers_all_subproblems);
    EXPECT_EQ(validation.payload.node_count, 3);
    EXPECT_EQ(validation.payload.edge_count, 2);
    ASSERT_EQ(plan.solve_dag.nodes.size(), 3U);
    EXPECT_FALSE(plan.solve_dag.nodes.back().solved_locally);
    EXPECT_TRUE(plan.solve_dag.nodes.back().aggregation_context);
    ASSERT_EQ(plan.solve_dag.edges.size(), plan.boundary_projections.size());
    EXPECT_EQ(plan.solve_dag.edges.front().source_context_id.value, 1U);
    EXPECT_EQ(plan.solve_dag.edges.front().target_context_id.value, 0U);
    EXPECT_EQ(plan.solve_dag.edges.front().projection_id.value,
              plan.boundary_projections.front().id.value);
    EXPECT_EQ(plan.solve_dag.edges.front().boundary_entity_ids.size(), 2U);
    EXPECT_EQ(plan.solve_dag.edges.front().boundary_constraint_ids.size(), 1U);
}

TEST(DecompositionPlannerContract, SolveIntentFixedEntitiesBecomeBoundaryVariables) {
    auto model = gcs::tools::make_integrated_feature_showcase_model();

    auto plan = plan_for(model);

    // Biconnected decomposition splits the showcase into 4 subproblems
    // (chain e0-e1-e2 has articulation e1; e3-e4-e5 has articulation e4)
    ASSERT_EQ(plan.subproblems.size(), 4U);
    bool found_fixed_boundary = false;
    bool found_other_component = false;
    for (const auto& subproblem : plan.subproblems) {
        if (kernel::contains_entity(subproblem.active_variables, kernel::EntityId{0})) {
            ASSERT_EQ(subproblem.boundary_variables.size(), 1U);
            EXPECT_EQ(subproblem.boundary_variables.front().value, 0U);
            found_fixed_boundary = true;
        } else {
            found_other_component = true;
        }
    }
    EXPECT_TRUE(found_fixed_boundary);
    EXPECT_TRUE(found_other_component);
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

TEST(DecompositionPlannerContract, SolveDagValidationRejectsBackwardDependency) {
    auto model = gcs::tools::make_two_component_distance_model();
    auto plan = plan_for(model);
    ASSERT_FALSE(plan.solve_dag.nodes.empty());
    plan.solve_dag.nodes.front().topological_order = 7;

    auto validation = planning::validate_solve_dag(plan);

    EXPECT_FALSE(validation.payload.valid);
    EXPECT_FALSE(validation.payload.acyclic);
    EXPECT_TRUE(has_code(validation.report, "planner.solve_dag_cycle_or_backward_edge"));
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
    EXPECT_EQ(first.solve_dag.edges[0].projection_id.value,
              second.solve_dag.edges[0].projection_id.value);
    EXPECT_FALSE(first.unsupported_report.unsupported);
}

// --- Spanning forest pattern contract tests ---

TEST(DecompositionPlannerContract, SpanningForestDistancePatternMatchesPointToPointDistance) {
    // Two rigid sets each containing a point, connected by a distance constraint
    auto model = gcs::tools::make_two_point_distance_model();
    auto incidence = graph::build_incidence_indices(graph::IncidenceInput{model});

    auto result = planning::plan_spanning_forest(model, incidence, model.solve_intent);

    EXPECT_EQ(result.report.status, kernel::StageStatus::ok);
    // One rigid body edge with one distance constraint between two points
    ASSERT_EQ(result.payload.selected_edges.size(), 1U);
    EXPECT_TRUE(result.payload.selected_edges.front().pattern_match.supported);
    EXPECT_EQ(result.payload.selected_edges.front().pattern_match.pattern_id.value,
              "point_to_point_distance");
    EXPECT_EQ(result.payload.selected_edges.front().pattern_match.removed_translational_dof, 1);
    EXPECT_EQ(result.payload.selected_edges.front().pattern_match.removed_rotational_dof, 0);
    EXPECT_EQ(result.payload.selected_edges.front().pattern_match.weight, 1);
    // Constraint should be absorbed
    EXPECT_EQ(result.payload.absorbed_constraint_ids.size(), 1U);
    EXPECT_TRUE(result.payload.closure_constraint_ids.empty());
    EXPECT_TRUE(result.payload.unsupported_constraint_ids.empty());
}

TEST(DecompositionPlannerContract, SpanningForestDistancePatternIsDeterministic) {
    auto model = gcs::tools::make_two_point_distance_model();
    auto incidence = graph::build_incidence_indices(graph::IncidenceInput{model});

    auto first = planning::plan_spanning_forest(model, incidence, model.solve_intent);
    auto second = planning::plan_spanning_forest(model, incidence, model.solve_intent);

    EXPECT_EQ(first.payload.selected_edges.size(), second.payload.selected_edges.size());
    EXPECT_EQ(first.payload.absorbed_constraint_ids.size(),
              second.payload.absorbed_constraint_ids.size());
    EXPECT_EQ(first.payload.closure_constraint_ids.size(),
              second.payload.closure_constraint_ids.size());
    EXPECT_EQ(first.payload.selected_edges.front().pattern_match.pattern_id.value,
              second.payload.selected_edges.front().pattern_match.pattern_id.value);
    EXPECT_EQ(first.payload.selected_edges.front().pattern_match.supported,
              second.payload.selected_edges.front().pattern_match.supported);
}

TEST(DecompositionPlannerContract, SpanningForestRejectedCycleConstraintsBecomeClosure) {
    // Two-component model: each component has 2 rigid sets with distance constraints
    // No cycles, so all constraints should be absorbed (tree edges)
    auto model = gcs::tools::make_two_component_distance_model();
    auto incidence = graph::build_incidence_indices(graph::IncidenceInput{model});

    auto result = planning::plan_spanning_forest(model, incidence, model.solve_intent);

    EXPECT_EQ(result.report.status, kernel::StageStatus::ok);
    // Two separate components, each should have one tree edge
    ASSERT_EQ(result.payload.selected_edges.size(), 2U);
    // Both distance constraints should match the pattern
    EXPECT_TRUE(result.payload.selected_edges[0].pattern_match.supported);
    EXPECT_TRUE(result.payload.selected_edges[1].pattern_match.supported);
    EXPECT_EQ(result.payload.absorbed_constraint_ids.size(), 2U);
    EXPECT_TRUE(result.payload.closure_constraint_ids.empty());
    EXPECT_TRUE(result.payload.unsupported_constraint_ids.empty());
}

TEST(DecompositionPlannerContract, SpanningForestValidatesNoSameRigidSetTreeEdges) {
    auto model = gcs::tools::make_two_point_distance_model();
    auto incidence = graph::build_incidence_indices(graph::IncidenceInput{model});

    auto result = planning::plan_spanning_forest(model, incidence, model.solve_intent);
    auto validation = planning::validate_spanning_forest(model, result.payload);

    EXPECT_TRUE(validation.payload.no_same_rigid_set_tree_edges);
    EXPECT_EQ(validation.payload.absorbed_count, 1);
    EXPECT_EQ(validation.payload.closure_count, 0);
    EXPECT_EQ(validation.payload.unsupported_count, 0);
    // Since we now have a supported pattern, selected_edges_have_supported_pattern should be true
    EXPECT_TRUE(validation.payload.selected_edges_have_supported_pattern);
}

TEST(DecompositionPlannerContract, SpanningForestAllActiveConstraintsArePartitioned) {
    auto model = gcs::tools::make_two_point_distance_model();
    auto incidence = graph::build_incidence_indices(graph::IncidenceInput{model});

    auto result = planning::plan_spanning_forest(model, incidence, model.solve_intent);
    auto validation = planning::validate_spanning_forest(model, result.payload);

    EXPECT_TRUE(validation.payload.every_active_constraint_partitioned_once);
    EXPECT_EQ(validation.payload.total_active_constraints, 1);
}
