import gcs.contract_tools;
import gcs.kernel;
import gcs.numeric_engine;
import gcs.session_runtime;
import gcs.viewer_bridge;

#include <gtest/gtest.h>

namespace {

namespace kernel = gcs::kernel;
namespace numeric = gcs::numeric;
namespace runtime = gcs::runtime;
namespace viewer = gcs::viewer;

bool has_overlay_code(const viewer::DiagnosticOverlay& overlay, const char* code) {
    for (const auto& item : overlay.items) {
        if (item.code == code) return true;
    }
    return false;
}

numeric::NumericTask make_boundary_frozen_task(kernel::ModelSnapshot model) {
    auto context = gcs::tools::make_whole_context_for(model);
    auto task = numeric::make_numeric_task(
        model,
        context,
        context.entity_ids,
        context.constraint_ids,
        kernel::GaugePolicy{});
    task.boundary_variables.push_back(kernel::EntityId{0});
    return task;
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
    ASSERT_EQ(overlay.payload.rank_evidence.size(), result.numeric_reports.size());
    ASSERT_FALSE(overlay.payload.rank_evidence.empty());
    EXPECT_EQ(overlay.payload.rank_evidence.front().numeric_variable_dimension, 6);
    EXPECT_EQ(overlay.payload.rank_evidence.front().numeric_free_variable_dimension, 6);
    EXPECT_EQ(overlay.payload.rank_evidence.front().numeric_frozen_variable_dimension, 0);
    EXPECT_TRUE(has_overlay_code(overlay.payload, "viewer.status"));
    EXPECT_TRUE(has_overlay_code(overlay.payload, "runtime.commit"));
    EXPECT_TRUE(has_overlay_code(overlay.payload, "viewer.rank_evidence"));
}

TEST(ViewerBridgeContract, OverlayProjectsBoundaryFrozenRankEvidence) {
    auto model = gcs::tools::make_two_point_distance_model();
    auto task = make_boundary_frozen_task(model);
    auto numeric_report = numeric::solve_local(task);

    runtime::CommandResult command_result;
    command_result.accepted = true;
    command_result.user_visible_status = kernel::SolveStatus::accepted_with_warnings;
    command_result.numeric_reports.push_back(numeric_report);

    auto overlay = viewer::build_overlay(
        viewer::DiagnosticOverlayRequest{
            model,
            command_result,
            viewer::DiagnosticVerbosity::detailed});

    ASSERT_EQ(overlay.payload.rank_evidence.size(), 1U);
    const auto& evidence = overlay.payload.rank_evidence.front();
    EXPECT_EQ(evidence.source, "runtime.numeric_rank_condition_report");
    EXPECT_EQ(evidence.local_report_index, 0);
    EXPECT_EQ(evidence.context_id.value, task.context_snapshot.id.value);
    EXPECT_EQ(evidence.result_status, kernel::SolveStatus::solved);
    EXPECT_EQ(evidence.numeric_variable_dimension, 6);
    EXPECT_EQ(evidence.numeric_free_variable_dimension, 3);
    EXPECT_EQ(evidence.numeric_frozen_variable_dimension, 3);
    EXPECT_EQ(evidence.numeric_residual_dimension, 1);
    EXPECT_EQ(evidence.numeric_rank_estimate, 1);
    EXPECT_EQ(evidence.numeric_nullity_estimate, 2);
    EXPECT_TRUE(evidence.numeric_under_constrained);
    EXPECT_FALSE(evidence.numeric_over_constrained);
    EXPECT_TRUE(has_overlay_code(overlay.payload, "viewer.rank_evidence"));

    auto summary = viewer::summarize_command_result(model, command_result);
    ASSERT_EQ(summary.rank_evidence.size(), 1U);
    EXPECT_EQ(summary.rank_evidence.front().numeric_frozen_variable_dimension, 3);
    ASSERT_FALSE(summary.messages.empty());
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
