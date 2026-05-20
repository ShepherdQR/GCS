module;

#include <string>
#include <vector>

export module gcs.io_adapters;

export import gcs.kernel;

export namespace gcs::io {

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

SceneLoadResult loadScene(const SceneLoadRequest& request);
SceneWriteResult writeSceneText(const SceneWriteRequest& request);
std::string summarizeScene(const ModelSnapshot& snapshot);

}
