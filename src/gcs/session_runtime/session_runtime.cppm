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
using gcs::kernel::SolveIntent;
using gcs::kernel::SolveStatus;
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

struct CommandResult {
    bool accepted = false;
    StateVersionId new_state_version;
    SolveStatus user_visible_status = SolveStatus::not_run;
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

    CommandResult execute(const Command& command);
    CommandResult solve(SolveIntent intent = SolveIntent{});

private:
    ModelSnapshot current_snapshot_;
    CommandId next_command_id_{1};

    Command make_solve_command(SolveIntent intent);
    void commit_accepted_state(const ProposedState& proposed_state);
};

}
