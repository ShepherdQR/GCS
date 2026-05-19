module;

#include <queue>
#include <unordered_set>
#include <vector>

module gcs.dcm;

import gcs.core;

namespace gcs {
namespace dcm {

void DecompositionManager::buildAdjacencyList(const Manager& m) {
    adjacencyList_.clear();
    for (const auto& g : m.geometries) {
        adjacencyList_[g.id] = {};
    }
    for (const auto& c : m.constraints) {
        for (size_t i = 0; i < c.geometryIds.size(); ++i) {
            for (size_t j = i + 1; j < c.geometryIds.size(); ++j) {
                int a = c.geometryIds[i];
                int b = c.geometryIds[j];
                adjacencyList_[a].push_back(b);
                adjacencyList_[b].push_back(a);
            }
        }
    }
    for (const auto& rs : m.rigidSets) {
        for (size_t i = 0; i < rs.geometryIds.size(); ++i) {
            for (size_t j = i + 1; j < rs.geometryIds.size(); ++j) {
                int a = rs.geometryIds[i];
                int b = rs.geometryIds[j];
                adjacencyList_[a].push_back(b);
                adjacencyList_[b].push_back(a);
            }
        }
    }
}

std::vector<int> DecompositionManager::bfsComponent(int startGeomId) {
    std::vector<int> component;
    std::queue<int> q;
    q.push(startGeomId);
    visited_.insert(startGeomId);

    while (!q.empty()) {
        int curr = q.front();
        q.pop();
        component.push_back(curr);

        auto it = adjacencyList_.find(curr);
        if (it != adjacencyList_.end()) {
            for (int neighbor : it->second) {
                if (visited_.find(neighbor) == visited_.end()) {
                    visited_.insert(neighbor);
                    q.push(neighbor);
                }
            }
        }
    }
    return component;
}

std::vector<std::vector<int>> DecompositionManager::findConnectedComponents() {
    std::vector<std::vector<int>> components;
    visited_.clear();

    for (const auto& [geomId, _] : adjacencyList_) {
        if (visited_.find(geomId) == visited_.end()) {
            components.push_back(bfsComponent(geomId));
        }
    }
    return components;
}

DecompositionResult DecompositionManager::decompose(const Manager& m) {
    DecompositionResult result;
    result.totalGeometries = static_cast<int>(m.geometries.size());
    result.totalConstraints = static_cast<int>(m.constraints.size());

    if (m.geometries.empty()) {
        result.isSingleComponent = true;
        return result;
    }

    buildAdjacencyList(m);
    auto components = findConnectedComponents();

    result.isSingleComponent = (components.size() <= 1);

    for (size_t i = 0; i < components.size(); ++i) {
        SubProblem sp;
        sp.id = static_cast<int>(i);
        sp.geometryIds = components[i];

        std::unordered_set<int> geomSet(components[i].begin(), components[i].end());

        for (const auto& c : m.constraints) {
            bool belongs = true;
            for (int gid : c.geometryIds) {
                if (geomSet.find(gid) == geomSet.end()) {
                    belongs = false;
                    break;
                }
            }
            if (belongs && !c.geometryIds.empty()) {
                sp.constraintIds.push_back(c.id);
            }
        }

        for (const auto& rs : m.rigidSets) {
            for (int gid : rs.geometryIds) {
                if (geomSet.find(gid) != geomSet.end()) {
                    sp.rigidSetIds.push_back(rs.id);
                    break;
                }
            }
        }

        result.subProblems.push_back(sp);
    }

    return result;
}

SubProblem DecompositionManager::extractSubProblem(
    const Manager& m, const std::vector<int>& geometryIds) const {
    SubProblem sp;
    sp.id = 0;
    sp.geometryIds = geometryIds;

    std::unordered_set<int> geomSet(geometryIds.begin(), geometryIds.end());

    for (const auto& c : m.constraints) {
        bool belongs = true;
        for (int gid : c.geometryIds) {
            if (geomSet.find(gid) == geomSet.end()) {
                belongs = false;
                break;
            }
        }
        if (belongs && !c.geometryIds.empty()) {
            sp.constraintIds.push_back(c.id);
        }
    }

    for (const auto& rs : m.rigidSets) {
        for (int gid : rs.geometryIds) {
            if (geomSet.find(gid) != geomSet.end()) {
                sp.rigidSetIds.push_back(rs.id);
                break;
            }
        }
    }

    return sp;
}

}
}
