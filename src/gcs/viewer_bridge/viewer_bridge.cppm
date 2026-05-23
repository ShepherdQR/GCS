module;

#include <cstdint>
#include <string>
#include <vector>

export module gcs.viewer_bridge;

export import gcs.kernel;
export import gcs.session_runtime;

export namespace gcs::viewer {

using gcs::kernel::ModelSnapshot;
using gcs::kernel::SolveStatus;

struct SnapshotSummary {
    int rigid_set_count = 0;
    int entity_count = 0;
    int constraint_count = 0;
    std::uint64_t state_version = 0;
    SolveStatus last_status = SolveStatus::not_run;
    std::vector<std::string> messages;
};

SnapshotSummary summarize_snapshot(const ModelSnapshot& snapshot);
SnapshotSummary summarize_command_result(const ModelSnapshot& snapshot,
                                         const runtime::CommandResult& result);
std::string solve_status_text(SolveStatus status);

}
