module;

#include <string>
#include <vector>

export module gcs.io_adapters;

export import gcs.kernel;

export namespace gcs::io {

using gcs::kernel::ModelSnapshot;

struct SceneLoadRequest {
    std::string path;
};

struct SceneLoadResult {
    bool ok = false;
    ModelSnapshot snapshot;
    std::vector<std::string> errors;
};

struct SceneWriteRequest {
    std::string path;
    ModelSnapshot snapshot;
};

struct SceneWriteResult {
    bool ok = false;
    std::vector<std::string> errors;
};

SceneLoadResult load_scene(const SceneLoadRequest& request);
SceneWriteResult write_scene_text(const SceneWriteRequest& request);
std::string summarize_scene(const ModelSnapshot& snapshot);

}
