#pragma once

#include "core/core.h"
#include <vector>
#include <unordered_map>
#include <unordered_set>

namespace gcs {
namespace dcm {

struct SubProblem {
    int id;
    std::vector<int> geometryIds;
    std::vector<int> constraintIds;
    std::vector<int> rigidSetIds;
};

struct DecompositionResult {
    std::vector<SubProblem> subProblems;
    int totalGeometries;
    int totalConstraints;
    bool isSingleComponent;
};

class DecompositionManager {
public:
    DecompositionManager() = default;

    DecompositionResult decompose(const Manager& m);

    SubProblem extractSubProblem(const Manager& m,
                                 const std::vector<int>& geometryIds) const;

private:
    void buildAdjacencyList(const Manager& m);
    std::vector<std::vector<int>> findConnectedComponents();
    std::vector<int> bfsComponent(int startGeomId);

    std::unordered_map<int, std::vector<int>> adjacencyList_;
    std::unordered_set<int> visited_;
};

}
}
