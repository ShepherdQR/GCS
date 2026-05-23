import gcs.contract_tools;
import gcs.kernel;
import gcs.session_runtime;

#include <gtest/gtest.h>

#include <cstddef>
#include <string>

namespace {

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
