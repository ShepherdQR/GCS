module;

#include <string>
#include <vector>

export module gcs.session_runtime;

export import gcs.kernel;
export import gcs.constraint_catalog;
export import gcs.incidence_graph;
export import gcs.decomposition_planner;
export import gcs.numeric_engine;
export import gcs.diagnostics;

export namespace gcs::runtime {

using gcs::kernel::CommandId;
using gcs::kernel::ModelSnapshot;
using gcs::kernel::ProposedState;
using gcs::kernel::ReportMessage;
using gcs::kernel::SolveIntent;
using gcs::kernel::SolveStatus;
using gcs::kernel::StageStatus;
using gcs::kernel::StageReport;
using gcs::kernel::StateVersionId;

enum class CommandKind {
    solve,
};

struct Command {
    CommandId id;
    CommandKind kind = CommandKind::solve;
    SolveIntent solve_intent;
    ModelSnapshot model_edit_or_solve_request;
};

struct CommandValidationReport {
    bool valid = true;
    bool supported_kind = true;
    bool command_id_present = true;
    bool request_base_version_matches = true;
    std::vector<ReportMessage> messages;
};

struct StageTraceEntry {
    int order = 0;
    std::string stage;
    StageStatus stage_status = StageStatus::ok;
    SolveStatus status = SolveStatus::not_run;
    StateVersionId before_version;
    StateVersionId after_version;
    bool durable_mutation = false;
    std::string code;
};

struct TransactionTrace {
    CommandId command_id;
    StateVersionId base_version;
    StateVersionId final_version;
    bool committed = false;
    bool rolled_back = false;
    std::string rollback_reason;
    std::vector<StageTraceEntry> stages;
};

struct RollbackReport {
    bool rolled_back = false;
    StateVersionId restored_version;
    std::string reason;
};

struct HistoryEvent {
    CommandId command_id;
    bool accepted = false;
    SolveStatus status = SolveStatus::not_run;
    StateVersionId base_version;
    StateVersionId new_state_version;
    TransactionTrace transaction_trace;
    std::vector<StageReport> stage_reports;
};

struct ReplayRequest {
    CommandId command_id;
};

struct ReplayReport {
    bool found = false;
    CommandId command_id;
    bool accepted = false;
    SolveStatus status = SolveStatus::not_run;
    TransactionTrace transaction_trace;
    std::vector<StageReport> stage_reports;
};

struct CommandResult {
    CommandId command_id;
    bool accepted = false;
    StateVersionId new_state_version;
    SolveStatus user_visible_status = SolveStatus::not_run;
    CommandValidationReport command_validation;
    TransactionTrace transaction_trace;
    RollbackReport rollback_report;
    std::vector<StageReport> stage_reports;
    planning::PlannerOutput planner_output;
    std::vector<numeric::NumericReport> numeric_reports;
    diagnostics::DiagnosticOutput pre_solve_diagnostics;
    diagnostics::GluingReport gluing_report;
    diagnostics::ObstructionReport obstruction_report;
};

class SessionRuntime {
public:
    SessionRuntime() = default;
    explicit SessionRuntime(ModelSnapshot snapshot);

    void load_snapshot(ModelSnapshot snapshot);
    const ModelSnapshot& current_snapshot() const;
    const std::vector<HistoryEvent>& history() const;

    CommandResult execute(const Command& command);
    CommandResult solve(SolveIntent intent = SolveIntent{});
    ReplayReport replay(ReplayRequest request) const;

private:
    ModelSnapshot current_snapshot_;
    CommandId next_command_id_{1};
    std::vector<HistoryEvent> history_;

    Command make_solve_command(SolveIntent intent);
    void commit_accepted_state(const ProposedState& proposed_state);
};

gcs::kernel::ContractResult<CommandValidationReport> validate_command(
    const ModelSnapshot& current_snapshot,
    const Command& command);

}
