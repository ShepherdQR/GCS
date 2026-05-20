module;

#include <string>
#include <vector>

export module gcs.viewer_bridge;

export import gcs.kernel;
export import gcs.session_runtime;

export namespace gcs::viewer {

struct SnapshotSummary {
    int rigidSetCount = 0;
    int entityCount = 0;
    int constraintCount = 0;
    int stateVersion = 0;
    SolveStatus lastStatus = SolveStatus::NotRun;
    std::vector<std::string> messages;
};

SnapshotSummary summarizeSnapshot(const ModelSnapshot& snapshot);
SnapshotSummary summarizeCommandResult(const ModelSnapshot& snapshot,
                                       const runtime::CommandResult& result);

}
