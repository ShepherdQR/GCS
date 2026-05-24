import gcs.io_adapters;
import gcs.session_runtime;
import gcs.viewer_bridge;

#include <fstream>
#include <iostream>
#include <string>

int main(int argc, char** argv) {
    std::string path = "fixtures/scene/basic/g1.txt";
    bool path_set = false;
    bool print_replay_evidence = false;
    bool save_replay_evidence = false;
    std::string replay_evidence_output_path;
    for (int index = 1; index < argc; ++index) {
        const std::string arg = argv[index];
        if (arg == "--help" || arg == "-h") {
            std::cout << "Usage: GCS.exe [scene-path] [--replay-evidence] "
                         "[--save-replay-evidence <path>]\n";
            return 0;
        }
        if (arg == "--replay-evidence") {
            print_replay_evidence = true;
            continue;
        }
        if (arg == "--save-replay-evidence") {
            if (index + 1 >= argc) {
                std::cerr << "--save-replay-evidence requires a path\n";
                return 1;
            }
            save_replay_evidence = true;
            replay_evidence_output_path = argv[++index];
            continue;
        }
        if (!path_set) {
            path = arg;
            path_set = true;
            continue;
        }
        std::cerr << "Unexpected argument: " << arg << "\n";
        return 1;
    }

    auto load_result = gcs::io::load_scene(gcs::io::SceneLoadRequest{path});
    if (!load_result.ok) {
        std::cerr << "Failed to load scene: " << path << "\n";
        for (const auto& error : load_result.errors) {
            std::cerr << "  " << error << "\n";
        }
        return 1;
    }

    gcs::runtime::SessionRuntime runtime(load_result.snapshot);
    auto result = runtime.solve(load_result.snapshot.solve_intent);
    auto summary = gcs::viewer::summarize_command_result(runtime.current_snapshot(), result);

    std::cout << "GCS C++23 canonical kernel solver skeleton\n";
    std::cout << "Input: " << path << "\n";
    std::cout << gcs::io::summarize_scene(runtime.current_snapshot()) << "\n";
    std::cout << "Status: " << gcs::viewer::solve_status_text(result.user_visible_status) << "\n";
    std::cout << "Accepted: " << (result.accepted ? "true" : "false") << "\n";
    std::cout << "New state version: " << result.new_state_version.value << "\n";
    std::cout << "Cover contexts: " << result.planner_output.cover_plan.contexts.size() << "\n";
    std::cout << "Local numeric reports: " << result.numeric_reports.size() << "\n";

    for (const auto& message : summary.messages) {
        std::cout << "  " << message << "\n";
    }

    if (print_replay_evidence || save_replay_evidence) {
        auto replay_evidence = runtime.export_replay_evidence(
            gcs::runtime::ReplayRequest{result.command_id});
        auto replay_artifact =
            gcs::viewer::build_replay_evidence_report_artifact(replay_evidence);
        if (print_replay_evidence) {
            std::cout << gcs::viewer::format_replay_evidence_summary(
                replay_artifact.payload.summary);
        }
        if (save_replay_evidence) {
            std::ofstream output(replay_evidence_output_path);
            if (!output) {
                std::cerr << "Failed to open replay evidence output: "
                          << replay_evidence_output_path << "\n";
                return 1;
            }
            output << gcs::viewer::format_replay_evidence_report_json(
                replay_artifact.payload);
            if (!output) {
                std::cerr << "Failed to write replay evidence output: "
                          << replay_evidence_output_path << "\n";
                return 1;
            }
        }
    }

    if (result.obstruction_report.present) {
        std::cerr << "Obstruction: " << result.obstruction_report.code << " - "
                  << result.obstruction_report.message << "\n";
        return 2;
    }

    return result.accepted ? 0 : 2;
}
