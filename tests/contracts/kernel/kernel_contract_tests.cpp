import gcs.kernel;

#include <gtest/gtest.h>

namespace {

namespace kernel = gcs::kernel;

kernel::ParameterVector pointParameters(double x, double y, double z) {
    kernel::ParameterVector parameters;
    parameters.dimension = kernel::geometry_dof(kernel::GeometryKind::point);
    parameters.values[0] = x;
    parameters.values[1] = y;
    parameters.values[2] = z;
    return parameters;
}

kernel::ModelDraft makeValidDraft() {
    kernel::ModelDraft draft;
    draft.rigid_sets.push_back(kernel::RigidSetDraft{kernel::RigidSetId{1}, {kernel::EntityId{10}}});
    draft.rigid_sets.push_back(kernel::RigidSetDraft{kernel::RigidSetId{2}, {kernel::EntityId{11}}});

    draft.entities.push_back(kernel::EntityDraft{
        kernel::EntityId{10},
        kernel::GeometryKind::point,
        kernel::RigidSetId{1},
        pointParameters(0.0, 0.0, 0.0)});
    draft.entities.push_back(kernel::EntityDraft{
        kernel::EntityId{11},
        kernel::GeometryKind::point,
        kernel::RigidSetId{2},
        pointParameters(1.0, 0.0, 0.0)});

    draft.constraints.push_back(kernel::ConstraintDraft{
        kernel::ConstraintId{20},
        kernel::ConstraintKind::distance,
        {kernel::EntityId{10}, kernel::EntityId{11}},
        1.0});
    return draft;
}

bool hasCode(const kernel::StageReport& report, const char* code) {
    for (const auto& message : report.messages) {
        if (message.code.value == code) return true;
    }
    return false;
}

}  // namespace

TEST(KernelContract, IdsAreStableAfterSnapshotCreation) {
    auto result = kernel::make_snapshot(makeValidDraft());

    EXPECT_EQ(result.report.status, kernel::StageStatus::ok);
    ASSERT_EQ(result.payload.entities.size(), 2);
    EXPECT_EQ(result.payload.entities[0].id.value, 10U);
    EXPECT_EQ(result.payload.entities[1].id.value, 11U);
    EXPECT_EQ(result.payload.state_version.value, 0U);
}

TEST(KernelContract, RejectsDuplicateEntityIds) {
    auto draft = makeValidDraft();
    draft.entities.push_back(draft.entities.front());

    auto result = kernel::make_snapshot(draft);

    EXPECT_EQ(result.report.status, kernel::StageStatus::error);
    EXPECT_TRUE(hasCode(result.report, "kernel.duplicate_entity_id"));
    EXPECT_FALSE(kernel::validate_model(result.payload).payload.valid);
}

TEST(KernelContract, RejectsMissingEntityReferences) {
    auto draft = makeValidDraft();
    draft.constraints.front().entity_ids.push_back(kernel::EntityId{99});

    auto result = kernel::make_snapshot(draft);

    EXPECT_EQ(result.report.status, kernel::StageStatus::error);
    EXPECT_TRUE(hasCode(result.report, "kernel.missing_entity"));
}

TEST(KernelContract, RejectsSolveIntentMissingReferences) {
    auto draft = makeValidDraft();
    draft.solve_intent.fixed_entity_ids.push_back(kernel::EntityId{99});
    draft.solve_intent.driven_entity_ids.push_back(kernel::EntityId{100});
    draft.solve_intent.target_constraint_ids.push_back(kernel::ConstraintId{101});

    auto result = kernel::make_snapshot(draft);

    EXPECT_EQ(result.report.status, kernel::StageStatus::error);
    EXPECT_TRUE(hasCode(result.report, "kernel.solve_intent_missing_fixed_entity"));
    EXPECT_TRUE(hasCode(result.report, "kernel.solve_intent_missing_driven_entity"));
    EXPECT_TRUE(hasCode(result.report, "kernel.solve_intent_missing_target_constraint"));
}

TEST(KernelContract, RejectsSolveIntentDuplicateReferences) {
    auto draft = makeValidDraft();
    draft.solve_intent.fixed_entity_ids = {kernel::EntityId{10}, kernel::EntityId{10}};
    draft.solve_intent.target_constraint_ids = {
        kernel::ConstraintId{20},
        kernel::ConstraintId{20}};

    auto result = kernel::make_snapshot(draft);

    EXPECT_EQ(result.report.status, kernel::StageStatus::error);
    EXPECT_TRUE(hasCode(result.report, "kernel.solve_intent_duplicate_fixed_entity"));
    EXPECT_TRUE(hasCode(result.report, "kernel.solve_intent_duplicate_target_constraint"));
}

TEST(KernelContract, RejectsInvalidParameterDimensions) {
    auto draft = makeValidDraft();
    draft.entities.front().parameters.dimension = 4;

    auto result = kernel::make_snapshot(draft);

    EXPECT_EQ(result.report.status, kernel::StageStatus::error);
    EXPECT_TRUE(hasCode(result.report, "kernel.invalid_parameter_dimension"));
}

TEST(KernelContract, WholeContextCoversAllSnapshotMembers) {
    auto snapshot = kernel::make_snapshot(makeValidDraft()).payload;

    auto context = kernel::make_context(snapshot, kernel::ContextRequest{kernel::ContextId{7}});
    auto validation = kernel::validate_context(snapshot, context.payload);

    EXPECT_EQ(context.report.status, kernel::StageStatus::ok);
    EXPECT_TRUE(validation.payload.valid);
    EXPECT_TRUE(validation.payload.covers_whole_model);
    EXPECT_EQ(context.payload.state_version.value, snapshot.state_version.value);
    EXPECT_EQ(context.payload.entity_ids.size(), snapshot.entities.size());
    EXPECT_EQ(context.payload.constraint_ids.size(), snapshot.constraints.size());
    EXPECT_EQ(context.payload.rigid_set_ids.size(), snapshot.rigid_sets.size());
}

TEST(KernelContract, StateDeltaRequiresMatchingBaseVersion) {
    auto snapshot = kernel::make_snapshot(makeValidDraft()).payload;
    kernel::StateDelta delta;
    delta.base_version = kernel::StateVersionId{99};
    delta.target_version = kernel::StateVersionId{100};
    delta.entity_states.push_back(kernel::EntityState{kernel::EntityId{10}, pointParameters(2.0, 0.0, 0.0)});

    auto validation = kernel::validate_delta(snapshot, delta);

    EXPECT_FALSE(validation.payload.valid);
    EXPECT_FALSE(validation.payload.base_version_matches);
    EXPECT_TRUE(hasCode(validation.report, "kernel.delta_base_version_mismatch"));
}

TEST(KernelContract, SnapshotDiffIsDeterministic) {
    auto before = kernel::make_snapshot(makeValidDraft()).payload;
    auto after = before;
    after.state_version = kernel::next_version(before.state_version);
    after.entities.front().parameters.values[0] = 3.0;
    after.entities.push_back(kernel::EntityDraft{
        kernel::EntityId{12},
        kernel::GeometryKind::point,
        kernel::RigidSetId{1},
        pointParameters(4.0, 0.0, 0.0)});

    auto first = kernel::diff_snapshots(before, after);
    auto second = kernel::diff_snapshots(before, after);

    ASSERT_EQ(first.payload.changed_entities.size(), 1);
    ASSERT_EQ(first.payload.added_entities.size(), 1);
    EXPECT_EQ(first.payload.changed_entities[0].value, 10U);
    EXPECT_EQ(first.payload.added_entities[0].value, 12U);
    EXPECT_EQ(first.payload.changed_entities[0].value, second.payload.changed_entities[0].value);
    EXPECT_TRUE(first.payload.state_version_changed);
}
