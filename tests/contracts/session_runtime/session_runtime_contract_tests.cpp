import gcs.contract_tools;
import gcs.kernel;
import gcs.session_runtime;

#include <gtest/gtest.h>

#include <cstddef>
#include <string>

namespace {

namespace diagnostics = gcs::diagnostics;
namespace kernel = gcs::kernel;
namespace runtime = gcs::runtime;

bool has_stage(const runtime::TransactionTrace& trace, const char* stage) {
    for (const auto& entry : trace.stages) {
        if (entry.stage == stage) return true;
    }
    return false;
}

int durable_mutation_count(const runtime::TransactionTrace& trace) {
    int count = 0;
    for (const auto& entry : trace.stages) {
        if (entry.durable_mutation) ++count;
    }
    return count;
}

bool has_report_code(const std::vector<std::string>& codes, const char* code) {
    for (const auto& candidate : codes) {
        if (candidate == code) return true;
    }
    return false;
}

runtime::Command make_external_solve_command(const kernel::ModelSnapshot& model,
                                             kernel::CommandId id) {
    runtime::Command command;
    command.id = id;
    command.kind = runtime::CommandKind::solve;
    command.solve_intent = model.solve_intent;
    command.model_edit_or_solve_request = model;
    return command;
}

}  // namespace

TEST(SessionRuntimeContract, RejectsInvalidCommandWithoutMutatingSnapshot) {
    auto model = gcs::tools::make_two_point_distance_model();
    runtime::SessionRuntime session(model);

    auto command = make_external_solve_command(model, kernel::CommandId{42});
    command.kind = static_cast<runtime::CommandKind>(999);

    auto result = session.execute(command);

    EXPECT_FALSE(result.accepted);
    EXPECT_FALSE(result.command_validation.valid);
    EXPECT_FALSE(result.command_validation.supported_kind);
    EXPECT_TRUE(result.rollback_report.rolled_back);
    EXPECT_EQ(result.rollback_report.restored_version.value, 0U);
    EXPECT_EQ(session.current_snapshot().state_version.value, 0U);
    EXPECT_FALSE(result.transaction_trace.committed);
    EXPECT_TRUE(result.transaction_trace.rolled_back);
    EXPECT_EQ(durable_mutation_count(result.transaction_trace), 0);
    EXPECT_EQ(session.history().size(), 1U);
}

TEST(SessionRuntimeContract, RollsBackWhenModelValidationFails) {
    auto model = gcs::tools::make_missing_entity_reference_model();
    runtime::SessionRuntime session(model);

    auto result = session.solve();

    EXPECT_FALSE(result.accepted);
    EXPECT_EQ(result.user_visible_status, kernel::SolveStatus::invalid_model);
    EXPECT_TRUE(result.rollback_report.rolled_back);
    EXPECT_EQ(session.current_snapshot().state_version.value, 0U);
    EXPECT_TRUE(has_stage(result.transaction_trace, "command_validation"));
    EXPECT_TRUE(has_stage(result.transaction_trace, "model_validation"));
    EXPECT_TRUE(has_stage(result.transaction_trace, "rollback"));
    EXPECT_FALSE(has_stage(result.transaction_trace, "planning"));
}

TEST(SessionRuntimeContract, AcceptedCommandAdvancesStateVersionOnce) {
    auto model = gcs::tools::make_two_point_distance_model();
    runtime::SessionRuntime session(model);

    auto result = session.solve();

    EXPECT_TRUE(result.accepted);
    EXPECT_TRUE(result.transaction_trace.committed);
    EXPECT_FALSE(result.transaction_trace.rolled_back);
    EXPECT_EQ(result.transaction_trace.base_version.value, 0U);
    EXPECT_EQ(result.transaction_trace.final_version.value, 1U);
    EXPECT_EQ(result.new_state_version.value, 1U);
    EXPECT_EQ(session.current_snapshot().state_version.value, 1U);
    EXPECT_EQ(durable_mutation_count(result.transaction_trace), 1);
    EXPECT_EQ(session.history().size(), 1U);
}

TEST(SessionRuntimeContract, ProjectsRankEvidenceFromAcceptedCommandResult) {
    auto model = gcs::tools::make_two_point_distance_model();
    runtime::SessionRuntime session(model);

    auto result = session.solve();
    auto rank_evidence = runtime::project_rank_evidence(result);

    ASSERT_EQ(rank_evidence.size(), result.numeric_reports.size());
    ASSERT_EQ(rank_evidence.size(), 1U);
    EXPECT_EQ(rank_evidence.front().source, "runtime.post_local_diagnostics.rank_report");
    EXPECT_EQ(rank_evidence.front().context_id.value, 0U);
    EXPECT_EQ(rank_evidence.front().result_status, kernel::SolveStatus::under_constrained);
    EXPECT_EQ(rank_evidence.front().numeric_variable_dimension, 6);
    EXPECT_EQ(rank_evidence.front().numeric_free_variable_dimension, 6);
    EXPECT_EQ(rank_evidence.front().numeric_frozen_variable_dimension, 0);
    EXPECT_EQ(rank_evidence.front().numeric_residual_dimension, 1);
    EXPECT_EQ(rank_evidence.front().numeric_rank_estimate, 1);
    EXPECT_EQ(rank_evidence.front().numeric_nullity_estimate, 5);
    EXPECT_TRUE(rank_evidence.front().numeric_under_constrained);
    EXPECT_FALSE(rank_evidence.front().numeric_over_constrained);
}

TEST(SessionRuntimeContract, PostLocalDiagnosticsPreserveNumericEvidence) {
    auto model = gcs::tools::make_two_point_distance_model();
    runtime::SessionRuntime session(model);

    auto result = session.solve();

    ASSERT_EQ(result.post_local_diagnostics.size(), result.numeric_reports.size());
    ASSERT_EQ(result.post_local_diagnostics.size(), 1U);
    const auto& post_local = result.post_local_diagnostics.front();
    EXPECT_EQ(post_local.local_report_index, 0);
    EXPECT_EQ(post_local.context_id.value, 0U);
    EXPECT_EQ(post_local.diagnostic_output.phase,
              diagnostics::DiagnosticPhase::post_local_solve);
    EXPECT_TRUE(post_local.diagnostic_output.residual_report.from_numeric_report);
    EXPECT_TRUE(post_local.diagnostic_output.residual_report.within_tolerance);
    EXPECT_EQ(post_local.diagnostic_output.rank_report.numeric_variable_dimension, 6);
    EXPECT_EQ(post_local.diagnostic_output.rank_report.numeric_free_variable_dimension, 6);
    EXPECT_EQ(post_local.diagnostic_output.rank_report.numeric_frozen_variable_dimension, 0);
    EXPECT_EQ(post_local.diagnostic_output.rank_report.numeric_rank_estimate, 1);
    EXPECT_EQ(post_local.diagnostic_output.rank_report.numeric_nullity_estimate, 5);
    EXPECT_TRUE(has_stage(result.transaction_trace, "post_local_diagnostics"));
}

TEST(SessionRuntimeContract, StageTraceIsCompleteForAcceptedSolve) {
    auto model = gcs::tools::make_two_point_distance_model();
    runtime::SessionRuntime session(model);

    auto result = session.solve();

    EXPECT_TRUE(has_stage(result.transaction_trace, "command_validation"));
    EXPECT_TRUE(has_stage(result.transaction_trace, "model_validation"));
    EXPECT_TRUE(has_stage(result.transaction_trace, "constraint_validation"));
    EXPECT_TRUE(has_stage(result.transaction_trace, "incidence_index"));
    EXPECT_TRUE(has_stage(result.transaction_trace, "planning"));
    EXPECT_TRUE(has_stage(result.transaction_trace, "pre_solve_diagnostics"));
    EXPECT_TRUE(has_stage(result.transaction_trace, "numeric_solve"));
    EXPECT_TRUE(has_stage(result.transaction_trace, "post_local_diagnostics"));
    EXPECT_TRUE(has_stage(result.transaction_trace, "gluing"));
    EXPECT_TRUE(has_stage(result.transaction_trace, "commit"));
    ASSERT_FALSE(result.transaction_trace.stages.empty());
    for (int index = 0; index < static_cast<int>(result.transaction_trace.stages.size());
         ++index) {
        EXPECT_EQ(result.transaction_trace.stages[static_cast<std::size_t>(index)].order,
                  index);
    }
}

TEST(SessionRuntimeContract, ReplayReturnsStoredStageTrace) {
    auto model = gcs::tools::make_two_point_distance_model();
    runtime::SessionRuntime session(model);

    auto result = session.solve();
    auto replay = session.replay(runtime::ReplayRequest{result.command_id});

    EXPECT_TRUE(replay.found);
    EXPECT_TRUE(replay.accepted);
    EXPECT_EQ(replay.status, result.user_visible_status);
    EXPECT_EQ(replay.transaction_trace.command_id.value, result.command_id.value);
    EXPECT_EQ(replay.transaction_trace.stages.size(), result.transaction_trace.stages.size());
    EXPECT_EQ(replay.stage_reports.size(), result.stage_reports.size());

    auto missing = session.replay(runtime::ReplayRequest{kernel::CommandId{999}});
    EXPECT_FALSE(missing.found);
}

TEST(SessionRuntimeContract, ReplayArtifactIsRuntimeTraceNotSceneConstructionHistory) {
    auto model = gcs::tools::make_two_point_distance_model();
    runtime::SessionRuntime session(model);

    auto result = session.solve();
    ASSERT_EQ(session.history().size(), 1U);
    const auto& event = session.history().front();

    EXPECT_EQ(event.replay_artifact_kind,
              runtime::ReplayArtifactKind::runtime_transaction_trace);
    EXPECT_TRUE(event.report_evidence);
    EXPECT_FALSE(event.scene_construction_history_entry);

    auto replay = session.replay(runtime::ReplayRequest{result.command_id});
    EXPECT_TRUE(replay.found);
    EXPECT_EQ(replay.replay_artifact_kind,
              runtime::ReplayArtifactKind::runtime_transaction_trace);
    EXPECT_TRUE(replay.report_evidence);
    EXPECT_FALSE(replay.scene_construction_history_entry);
    EXPECT_EQ(replay.transaction_trace.command_id.value, result.command_id.value);
}

TEST(SessionRuntimeContract, ReplayEvidenceExportIsDeterministicReportEvidence) {
    auto model = gcs::tools::make_two_point_distance_model();
    runtime::SessionRuntime session(model);

    auto result = session.solve();
    auto first = session.export_replay_evidence(
        runtime::ReplayRequest{result.command_id});
    auto second = session.export_replay_evidence(
        runtime::ReplayRequest{result.command_id});

    EXPECT_TRUE(first.found);
    EXPECT_TRUE(first.report_evidence);
    EXPECT_FALSE(first.scene_construction_history_entry);
    EXPECT_EQ(first.replay_artifact_kind,
              runtime::ReplayArtifactKind::runtime_transaction_trace);
    EXPECT_EQ(first.command_id.value, result.command_id.value);
    EXPECT_EQ(first.accepted, result.accepted);
    EXPECT_EQ(first.status, result.user_visible_status);
    EXPECT_EQ(first.base_version.value, 0U);
    EXPECT_EQ(first.final_version.value, 1U);
    EXPECT_TRUE(first.committed);
    EXPECT_FALSE(first.rolled_back);

    ASSERT_EQ(first.stages.size(), second.stages.size());
    ASSERT_EQ(first.stages.size(), result.transaction_trace.stages.size());
    for (int index = 0; index < static_cast<int>(first.stages.size());
         ++index) {
        const auto& first_stage =
            first.stages[static_cast<std::size_t>(index)];
        const auto& second_stage =
            second.stages[static_cast<std::size_t>(index)];
        EXPECT_EQ(first_stage.order, index);
        EXPECT_EQ(first_stage.order, second_stage.order);
        EXPECT_EQ(first_stage.stage, second_stage.stage);
        EXPECT_EQ(first_stage.report_code, second_stage.report_code);
        EXPECT_NE(first_stage.stage, "AddRigidSet");
        EXPECT_NE(first_stage.stage, "AddGeometry");
        EXPECT_NE(first_stage.stage, "AddConstraint");
        EXPECT_NE(first_stage.stage, "UpdateConstraint");
        EXPECT_NE(first_stage.stage, "Solve");
    }

    EXPECT_TRUE(has_report_code(first.report_codes, "runtime.commit"));
}

TEST(SessionRuntimeContract, ReplayEvidenceExportReportsMissingCommand) {
    auto model = gcs::tools::make_two_point_distance_model();
    runtime::SessionRuntime session(model);

    auto missing = session.export_replay_evidence(
        runtime::ReplayRequest{kernel::CommandId{999}});

    EXPECT_FALSE(missing.found);
    EXPECT_TRUE(missing.report_evidence);
    EXPECT_FALSE(missing.scene_construction_history_entry);
    EXPECT_EQ(missing.replay_artifact_kind,
              runtime::ReplayArtifactKind::runtime_transaction_trace);
    EXPECT_EQ(missing.command_id.value, 999U);
    EXPECT_FALSE(missing.accepted);
    EXPECT_EQ(missing.status, kernel::SolveStatus::not_run);
    EXPECT_TRUE(missing.stages.empty());
    ASSERT_EQ(missing.report_codes.size(), 1U);
    EXPECT_EQ(missing.report_codes.front(), "runtime.replay_missing_command");
}
