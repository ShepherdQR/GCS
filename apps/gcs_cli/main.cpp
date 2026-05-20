import gcs.io_adapters;
import gcs.session_runtime;
import gcs.viewer_bridge;

#include <iostream>
#include <string>

int main(int argc, char** argv) {
    std::string path = "fixtures/scene/basic/g1.txt";
    if (argc > 1) {
        path = argv[1];
    }

    auto loadResult = gcs::io::loadScene(gcs::io::SceneLoadRequest{path});
    if (!loadResult.ok) {
        std::cerr << "Failed to load scene: " << path << "\n";
        for (const auto& error : loadResult.errors) {
            std::cerr << "  " << error << "\n";
        }
        return 1;
    }

    gcs::runtime::SessionRuntime runtime(loadResult.snapshot);
    auto result = runtime.solve(loadResult.snapshot.solveIntent);
    auto summary = gcs::viewer::summarizeCommandResult(runtime.currentSnapshot(), result);

    std::cout << "GCS C++23 module solver skeleton\n";
    std::cout << "Input: " << path << "\n";
    std::cout << gcs::io::summarizeScene(runtime.currentSnapshot()) << "\n";
    std::cout << "Status: " << gcs::toString(result.userVisibleStatus) << "\n";
    std::cout << "Accepted: " << (result.accepted ? "true" : "false") << "\n";
    std::cout << "New state version: " << result.newStateVersion.value << "\n";
    std::cout << "Cover contexts: " << result.plannerOutput.coverPlan.contexts.size() << "\n";
    std::cout << "Local numeric reports: " << result.numericReports.size() << "\n";

    for (const auto& message : summary.messages) {
        std::cout << "  " << message << "\n";
    }

    if (result.obstructionReport.present) {
        std::cerr << "Obstruction: " << result.obstructionReport.code << " - "
                  << result.obstructionReport.message << "\n";
        return 2;
    }

    return result.accepted ? 0 : 2;
}
