import gcs.diagnostics;
import gcs.contract_tools;
import gcs.kernel;
import gcs.numeric_engine;
import gcs.session_runtime;
import gcs.viewer_bridge;

#include <gtest/gtest.h>

namespace {

namespace kernel = gcs::kernel;
namespace diagnostics = gcs::diagnostics;
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

diagnostics::DiagnosticOutput diagnose_after_local_solve(
    const kernel::ModelSnapshot& model,
    const numeric::NumericTask& task,
    const numeric::NumericReport& numeric_report) {
    diagnostics::DiagnosticInput input;
    input.phase = diagnostics::DiagnosticPhase::post_local_solve;
    input.model = model;
    input.context = task.context_snapshot;
    input.numeric_report = numeric_report;
    input.gauge_policy = kernel::GaugePolicy{};
    return diagnostics::diagnose(input);
}

runtime::CommandResult make_post_local_command_result(
    const numeric::NumericTask& task,
    const numeric::NumericReport& numeric_report,
    diagnostics::DiagnosticOutput diagnostic_output) {
    runtime::CommandResult command_result;
    command_result.accepted = numeric_report.result_code == kernel::SolveStatus::solved;
    command_result.user_visible_status = diagnostic_output.status_code;
    command_result.numeric_reports.push_back(numeric_report);
    command_result.post_local_diagnostics.push_back(
        runtime::PostLocalDiagnosticReport{
            0,
            task.context_snapshot.id,
            diagnostic_output});
    return command_result;
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

TEST(ViewerBridgeContract, OverlayProjectsResidualAndConflictEvidence) {
    auto model = gcs::tools::make_unsatisfied_two_point_distance_model();
    auto context = gcs::tools::make_whole_context_for(model);
    auto task = numeric::make_numeric_task(
        model,
        context,
        context.entity_ids,
        context.constraint_ids,
        kernel::GaugePolicy{});
    task.solve_limits.max_iterations = 0;
    auto numeric_report = numeric::solve_local(task);
    auto diagnostic_output =
        diagnose_after_local_solve(model, task, numeric_report);
    auto command_result = make_post_local_command_result(
        task,
        numeric_report,
        diagnostic_output);

    auto overlay = viewer::build_overlay(
        viewer::DiagnosticOverlayRequest{
            model,
            command_result,
            viewer::DiagnosticVerbosity::detailed});

    ASSERT_EQ(overlay.payload.residual_evidence.size(), 1U);
    const auto& residual = overlay.payload.residual_evidence.front();
    EXPECT_EQ(residual.source, "runtime.post_local_diagnostics.residual_report");
    EXPECT_FALSE(residual.within_tolerance);
    EXPECT_EQ(residual.residual_dimension, 1);
    ASSERT_EQ(residual.constraints.size(), 1U);
    EXPECT_EQ(residual.constraints.front().constraint_id.value, 0U);
    EXPECT_FALSE(residual.constraints.front().satisfied);

    ASSERT_EQ(overlay.payload.conflict_evidence.size(), 1U);
    const auto& conflict = overlay.payload.conflict_evidence.front();
    EXPECT_EQ(conflict.source, "runtime.post_local_diagnostics.conflict_sets");
    EXPECT_EQ(conflict.code, "diagnostics.residual_conflict");
    ASSERT_EQ(conflict.entity_ids.size(), 2U);
    EXPECT_EQ(conflict.entity_ids[0].value, 0U);
    EXPECT_EQ(conflict.entity_ids[1].value, 1U);
    ASSERT_EQ(conflict.constraint_ids.size(), 1U);
    EXPECT_EQ(conflict.constraint_ids.front().value, 0U);
    EXPECT_TRUE(has_overlay_code(overlay.payload, "viewer.residual_evidence"));
    EXPECT_TRUE(has_overlay_code(overlay.payload, "viewer.conflict_evidence"));

    auto summary = viewer::summarize_command_result(model, command_result);
    ASSERT_EQ(summary.residual_evidence.size(), 1U);
    ASSERT_EQ(summary.conflict_evidence.size(), 1U);
}

TEST(ViewerBridgeContract, OverlayProjectsRedundancyEvidence) {
    auto model = gcs::tools::make_redundant_distance_pair_model();
    auto context = gcs::tools::make_whole_context_for(model);
    auto task = numeric::make_numeric_task(
        model,
        context,
        context.entity_ids,
        context.constraint_ids,
        kernel::GaugePolicy{});
    auto numeric_report = numeric::solve_local(task);
    auto diagnostic_output =
        diagnose_after_local_solve(model, task, numeric_report);
    auto command_result = make_post_local_command_result(
        task,
        numeric_report,
        diagnostic_output);

    auto overlay = viewer::build_overlay(
        viewer::DiagnosticOverlayRequest{
            model,
            command_result,
            viewer::DiagnosticVerbosity::detailed});

    ASSERT_EQ(overlay.payload.redundancy_evidence.size(), 1U);
    const auto& redundancy = overlay.payload.redundancy_evidence.front();
    EXPECT_EQ(redundancy.source,
              "runtime.post_local_diagnostics.redundancy_sets");
    EXPECT_EQ(redundancy.code, "diagnostics.redundant_duplicate_distance");
    ASSERT_EQ(redundancy.constraint_ids.size(), 2U);
    EXPECT_EQ(redundancy.constraint_ids[0].value, 0U);
    EXPECT_EQ(redundancy.constraint_ids[1].value, 1U);
    EXPECT_TRUE(has_overlay_code(overlay.payload, "viewer.redundancy_evidence"));

    auto summary = viewer::summarize_command_result(model, command_result);
    ASSERT_EQ(summary.redundancy_evidence.size(), 1U);
}

TEST(ViewerBridgeContract, ShowcaseFixtureProjectsBoundaryRankAndResidualEvidence) {
    auto model = gcs::tools::make_integrated_feature_showcase_model();
    runtime::SessionRuntime session(model);

    auto result = session.solve(model.solve_intent);

    EXPECT_TRUE(result.accepted);
    EXPECT_EQ(result.user_visible_status, kernel::SolveStatus::accepted_with_warnings);
    ASSERT_EQ(result.planner_output.subproblems.size(), 2U);
    ASSERT_EQ(result.numeric_reports.size(), 2U);
    ASSERT_EQ(result.post_local_diagnostics.size(), 2U);

    auto overlay = viewer::build_overlay(
        viewer::DiagnosticOverlayRequest{
            session.current_snapshot(),
            result,
            viewer::DiagnosticVerbosity::detailed});

    ASSERT_EQ(overlay.payload.rank_evidence.size(), 2U);
    bool found_frozen_rank = false;
    bool found_unfrozen_rank = false;
    for (const auto& evidence : overlay.payload.rank_evidence) {
        EXPECT_EQ(evidence.source, "runtime.post_local_diagnostics.rank_report");
        if (evidence.numeric_frozen_variable_dimension > 0) {
            found_frozen_rank = true;
            EXPECT_EQ(evidence.numeric_variable_dimension, 9);
            EXPECT_EQ(evidence.numeric_frozen_variable_dimension, 3);
            EXPECT_EQ(evidence.numeric_free_variable_dimension, 6);
        } else {
            found_unfrozen_rank = true;
        }
    }
    EXPECT_TRUE(found_frozen_rank);
    EXPECT_TRUE(found_unfrozen_rank);

    ASSERT_GE(overlay.payload.residual_evidence.size(), 2U);
    EXPECT_TRUE(overlay.payload.redundancy_evidence.empty());
    EXPECT_TRUE(has_overlay_code(overlay.payload, "viewer.rank_evidence"));
    EXPECT_TRUE(has_overlay_code(overlay.payload, "viewer.residual_evidence"));

    auto summary = viewer::summarize_command_result(session.current_snapshot(), result);
    ASSERT_EQ(summary.rank_evidence.size(), 2U);
    ASSERT_GE(summary.residual_evidence.size(), 2U);
}

TEST(ViewerBridgeContract, OverlayProjectsGluingObstructionEvidence) {
    auto model = gcs::tools::make_two_point_distance_model();
    runtime::CommandResult command_result;
    command_result.user_visible_status = kernel::SolveStatus::inconsistent;
    command_result.obstruction_report.present = true;
    command_result.obstruction_report.code = "gluing.boundary_projection_mismatch";
    command_result.obstruction_report.message =
        "Local sections disagree on a declared boundary projection.";
    command_result.obstruction_report.entity_ids = {kernel::EntityId{0}};
    command_result.obstruction_report.constraint_ids = {kernel::ConstraintId{0}};
    command_result.gluing_report.conflict_sets.push_back(
        diagnostics::ConflictSet{
            "gluing.boundary_projection_mismatch",
            {kernel::EntityId{0}},
            {kernel::ConstraintId{0}}});

    auto overlay = viewer::build_overlay(
        viewer::DiagnosticOverlayRequest{
            model,
            command_result,
            viewer::DiagnosticVerbosity::detailed});

    ASSERT_EQ(overlay.payload.obstruction_evidence.size(), 1U);
    EXPECT_EQ(overlay.payload.obstruction_evidence.front().source,
              "runtime.obstruction_report");
    EXPECT_EQ(overlay.payload.obstruction_evidence.front().code,
              "gluing.boundary_projection_mismatch");
    ASSERT_EQ(overlay.payload.conflict_evidence.size(), 1U);
    EXPECT_EQ(overlay.payload.conflict_evidence.front().source,
              "runtime.gluing.conflict_sets");
    EXPECT_TRUE(has_overlay_code(overlay.payload, "viewer.obstruction_evidence"));
    EXPECT_TRUE(has_overlay_code(overlay.payload, "viewer.conflict_evidence"));
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

TEST(ViewerBridgeContract, RuntimeHistoryFrameProjectsAsReportEvidenceOnly) {
    auto model = gcs::tools::make_two_point_distance_model();
    runtime::SessionRuntime session(model);
    auto result = session.solve();
    ASSERT_EQ(session.history().size(), 1U);

    auto frame = viewer::project_history_frame(
        viewer::HistoryFrameRequest{session.history().front(), 0});

    EXPECT_TRUE(frame.payload.valid);
    EXPECT_EQ(frame.payload.command_id.value, result.command_id.value);
    EXPECT_EQ(frame.payload.replay_artifact_kind,
              runtime::ReplayArtifactKind::runtime_transaction_trace);
    EXPECT_TRUE(frame.payload.report_evidence);
    EXPECT_FALSE(frame.payload.scene_construction_history_entry);

    ASSERT_FALSE(frame.payload.stages.empty());
    for (const auto& stage : frame.payload.stages) {
        EXPECT_NE(stage.stage, "AddRigidSet");
        EXPECT_NE(stage.stage, "AddGeometry");
        EXPECT_NE(stage.stage, "AddConstraint");
        EXPECT_NE(stage.stage, "UpdateConstraint");
        EXPECT_NE(stage.stage, "Solve");
    }
}
