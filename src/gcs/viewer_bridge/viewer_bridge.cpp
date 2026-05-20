module;

#include <string>

module gcs.viewer_bridge;

import gcs.kernel;
import gcs.session_runtime;

namespace gcs::viewer {

SnapshotSummary summarizeSnapshot(const ModelSnapshot& snapshot) {
    SnapshotSummary summary;
    summary.rigidSetCount = static_cast<int>(snapshot.rigidSets.size());
    summary.entityCount = static_cast<int>(snapshot.entities.size());
    summary.constraintCount = static_cast<int>(snapshot.constraints.size());
    summary.stateVersion = snapshot.stateVersion.value;
    return summary;
}

SnapshotSummary summarizeCommandResult(const ModelSnapshot& snapshot,
                                       const runtime::CommandResult& result) {
    SnapshotSummary summary = summarizeSnapshot(snapshot);
    summary.lastStatus = result.userVisibleStatus;
    for (const auto& report : result.stageReports) {
        summary.messages.push_back(report.stage + ": " + toString(report.status));
        for (const auto& message : report.messages) {
            summary.messages.push_back(message.code + ": " + message.message);
        }
    }
    if (result.obstructionReport.present) {
        summary.messages.push_back(result.obstructionReport.code + ": " +
                                   result.obstructionReport.message);
    }
    return summary;
}

}
