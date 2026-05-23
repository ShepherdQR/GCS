import gcs.contract_tools;
import gcs.kernel;
import gcs.session_runtime;
import gcs.viewer_bridge;

#include <gtest/gtest.h>

namespace {

namespace kernel = gcs::kernel;
namespace runtime = gcs::runtime;
namespace viewer = gcs::viewer;

bool has_overlay_code(const viewer::DiagnosticOverlay& overlay, const char* code) {
    for (const auto& item : overlay.items) {
        if (item.code == code) return true;
    }
    return false;
}

}  // namespace

TEST(ViewerBridgeContract, ProjectionIsDeterministic) {
    auto model = gcs::tools::make_two_point_distance_model();
    viewer::ViewerProjectionRequest request;
    request.snapshot = model;
    request.selected_entities = {kernel::EntityId{0}};
    request.selected_constraints = {kernel::ConstraintId{0}};

    auto first = viewer::project_scene(request);
    auto second = viewer::project_scene(request);

    ASSERT_EQ(first.payload.entities.size(), second.payload.entities.size());
    ASSERT_EQ(first.payload.constraints.size(), second.payload.constraints.size());
    EXPECT_EQ(first.payload.entities.front().id.value, second.payload.entities.front().id.value);
    EXPECT_TRUE(first.payload.entities.front().selected);
    EXPECT_TRUE(first.payload.constraints.front().selected);
    EXPECT_EQ(first.payload.constraints.front().entity_ids.size(),
              second.payload.constraints.front().entity_ids.size());
}

TEST(ViewerBridgeContract, ProjectionContainsStateVersion) {
    auto model = gcs::tools::make_two_point_distance_model();
    model.state_version = kernel::StateVersionId{12};

    auto projection = viewer::project_scene(viewer::ViewerProjectionRequest{model});

    EXPECT_EQ(projection.payload.state_version.value, 12U);
    EXPECT_EQ(projection.payload.schema_version, model.schema_version);
    EXPECT_EQ(projection.payload.rigid_set_count, 2);
}

TEST(ViewerBridgeContract, OverlayDerivesStatusFromCommandResult) {
    auto model = gcs::tools::make_two_point_distance_model();
    runtime::SessionRuntime session(model);
    auto result = session.solve();

    auto overlay = viewer::build_overlay(
        viewer::DiagnosticOverlayRequest{
            session.current_snapshot(),
            result,
            viewer::DiagnosticVerbosity::detailed});

    EXPECT_TRUE(overlay.payload.accepted);
    EXPECT_EQ(overlay.payload.status, result.user_visible_status);
    EXPECT_TRUE(has_overlay_code(overlay.payload, "viewer.status"));
    EXPECT_TRUE(has_overlay_code(overlay.payload, "runtime.commit"));
}

TEST(ViewerBridgeContract, CommandDraftValidatesAgainstRuntimeContract) {
    auto model = gcs::tools::make_two_point_distance_model();
    viewer::InteractionDraftRequest request;
    request.snapshot = model;
    request.command_id = kernel::CommandId{77};
    request.solve_intent = model.solve_intent;

    auto draft = viewer::draft_command(request);
    auto validation = runtime::validate_command(model, draft.payload.command);

    EXPECT_TRUE(draft.payload.valid);
    EXPECT_TRUE(validation.payload.valid);
    EXPECT_EQ(draft.payload.command.id.value, 77U);
    EXPECT_EQ(draft.payload.command.model_edit_or_solve_request.state_version.value,
              model.state_version.value);
}

TEST(ViewerBridgeContract, HistoryFrameResolvesStableIds) {
    auto model = gcs::tools::make_two_point_distance_model();
    runtime::SessionRuntime session(model);
    auto result = session.solve();
    ASSERT_EQ(session.history().size(), 1U);

    auto frame = viewer::project_history_frame(
        viewer::HistoryFrameRequest{session.history().front(), 0});

    EXPECT_TRUE(frame.payload.valid);
    EXPECT_EQ(frame.payload.command_id.value, result.command_id.value);
    EXPECT_EQ(frame.payload.base_version.value, 0U);
    EXPECT_EQ(frame.payload.new_state_version.value, 1U);
    EXPECT_FALSE(frame.payload.stages.empty());
}
