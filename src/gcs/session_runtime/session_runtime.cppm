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

enum class CommandKind {
    Solve,
};

struct Command {
    CommandId id;
    CommandKind kind = CommandKind::Solve;
    SolveIntent solveIntent;
    ModelSnapshot modelEditOrSolveRequest;
};

struct CommandResult {
    bool accepted = false;
    StateVersionId newStateVersion;
    SolveStatus userVisibleStatus = SolveStatus::NotRun;
    std::vector<StageReport> stageReports;
    planning::PlannerOutput plannerOutput;
    std::vector<numeric::NumericReport> numericReports;
    diagnostics::DiagnosticOutput preSolveDiagnostics;
    diagnostics::GluingReport gluingReport;
    diagnostics::ObstructionReport obstructionReport;
};

class SessionRuntime {
public:
    SessionRuntime() = default;
    explicit SessionRuntime(ModelSnapshot snapshot);

    void loadSnapshot(ModelSnapshot snapshot);
    const ModelSnapshot& currentSnapshot() const;

    CommandResult execute(const Command& command);
    CommandResult solve(SolveIntent intent = SolveIntent{});

private:
    ModelSnapshot currentSnapshot_;
    CommandId nextCommandId_{1};

    Command makeSolveCommand(SolveIntent intent);
    void commitAcceptedState(const ProposedState& proposedState);
};

}
