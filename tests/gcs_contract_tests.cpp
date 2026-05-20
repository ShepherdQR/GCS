import gcs.kernel;
import gcs.constraint_catalog;
import gcs.incidence_graph;
import gcs.decomposition_planner;
import gcs.session_runtime;
import gcs.contract_tools;

#include <gtest/gtest.h>

TEST(KernelContracts, SnapshotKeepsStableEntityIdentity) {
    auto model = gcs::tools::makeTwoPointDistanceModel();

    const auto* entity = gcs::findEntity(model, gcs::EntityId{1});

    ASSERT_NE(entity, nullptr);
    EXPECT_EQ(entity->id.value, 1);
    EXPECT_EQ(entity->rigidSetId.value, 1);
    EXPECT_EQ(gcs::geometryDof(entity->kind), 3);
}

TEST(ConstraintCatalogContracts, ValidatesBuiltInDistanceConstraint) {
    auto model = gcs::tools::makeTwoPointDistanceModel();
    const auto& constraint = model.constraints.front();

    auto result = gcs::constraints::validateConstraint(
        gcs::constraints::ConstraintValidationInput{model, constraint});

    EXPECT_TRUE(result.valid);
    EXPECT_EQ(result.definition.residualDimension, 1);
    EXPECT_TRUE(result.messages.empty());
}

TEST(PlanningContracts, ProducesCoverAndSubproblem) {
    auto model = gcs::tools::makeTwoPointDistanceModel();
    auto incidence = gcs::graph::buildIncidenceIndices(gcs::graph::IncidenceInput{model});
    auto plan = gcs::planning::planDecomposition(
        gcs::planning::PlannerInput{model, incidence, model.solveIntent, {}});

    EXPECT_FALSE(plan.coverPlan.contexts.empty());
    EXPECT_FALSE(plan.subproblems.empty());
    EXPECT_EQ(plan.coverPlan.rootContextId.value, 0);
}

TEST(RuntimeContracts, SolveProducesAcceptedGluingReport) {
    auto model = gcs::tools::makeTwoPointDistanceModel();
    gcs::runtime::SessionRuntime runtime(model);

    auto result = runtime.solve();

    EXPECT_TRUE(result.accepted);
    EXPECT_TRUE(result.gluingReport.accepted);
    EXPECT_FALSE(result.gluingReport.obstructionReport.present);
    EXPECT_EQ(runtime.currentSnapshot().stateVersion.value, 1);
}
