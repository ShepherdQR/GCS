module;

#include <string>

module gcs.viewer_bridge;

import gcs.kernel;
import gcs.session_runtime;

namespace gcs::viewer {

namespace kernel = gcs::kernel;

SnapshotSummary summarize_snapshot(const ModelSnapshot& snapshot) {
    SnapshotSummary summary;
    summary.rigid_set_count = static_cast<int>(snapshot.rigid_sets.size());
    summary.entity_count = static_cast<int>(snapshot.entities.size());
    summary.constraint_count = static_cast<int>(snapshot.constraints.size());
    summary.state_version = snapshot.state_version.value;
    return summary;
}

SnapshotSummary summarize_command_result(const ModelSnapshot& snapshot,
                                         const runtime::CommandResult& result) {
    SnapshotSummary summary = summarize_snapshot(snapshot);
    summary.last_status = result.user_visible_status;
    for (const auto& report : result.stage_reports) {
        summary.messages.push_back(report.stage + ": " + kernel::to_string(report.status));
        for (const auto& message : report.messages) {
            summary.messages.push_back(message.code.value + ": " + message.summary);
        }
    }
    if (result.obstruction_report.present) {
        summary.messages.push_back(result.obstruction_report.code + ": " +
                                   result.obstruction_report.message);
    }
    return summary;
}

std::string solve_status_text(SolveStatus status) {
    return kernel::to_string(status);
}

}
