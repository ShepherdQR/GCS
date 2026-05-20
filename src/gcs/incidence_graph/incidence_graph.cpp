module;

#include <queue>
#include <cstddef>
#include <vector>

module gcs.incidence_graph;

import gcs.kernel;

namespace gcs::graph {

namespace {

int entityIndex(const ModelSnapshot& model, EntityId entityId) {
    for (int i = 0; i < static_cast<int>(model.entities.size()); ++i) {
        if (model.entities[static_cast<std::size_t>(i)].id == entityId) return i;
    }
    return -1;
}

bool componentContains(const ConnectedComponent& component, EntityId entityId) {
    return containsEntity(component.entityIds, entityId);
}

}

IncidenceIndices buildIncidenceIndices(const IncidenceInput& input) {
    IncidenceIndices indices;
    indices.report = makeStageReport("incidence_graph.build_indices");

    const auto& model = input.model;
    indices.entityIncidence.reserve(model.entities.size());
    for (const auto& entity : model.entities) {
        indices.entityIncidence.push_back(EntityIncidence{entity.id, {}});
    }

    std::vector<std::vector<int>> adjacency(model.entities.size());
    for (const auto& constraint : model.constraints) {
        std::vector<int> incidentEntityIndexes;
        for (EntityId entityId : constraint.entityIds) {
            int index = entityIndex(model, entityId);
            if (index < 0) {
                ReportMessage message;
                message.severity = ReportSeverity::Error;
                message.code = "incidence.missing_entity";
                message.message = "Constraint references an entity missing from incidence indices.";
                message.constraintIds.push_back(constraint.id);
                message.entityIds.push_back(entityId);
                indices.report.messages.push_back(message);
                indices.report.status = StageStatus::Error;
                continue;
            }
            indices.entityIncidence[static_cast<std::size_t>(index)].constraintIds.push_back(constraint.id);
            incidentEntityIndexes.push_back(index);
        }

        for (int lhs : incidentEntityIndexes) {
            for (int rhs : incidentEntityIndexes) {
                if (lhs != rhs) adjacency[static_cast<std::size_t>(lhs)].push_back(rhs);
            }
        }
    }

    std::vector<bool> visited(model.entities.size(), false);
    int componentIndex = 0;
    for (int start = 0; start < static_cast<int>(model.entities.size()); ++start) {
        if (visited[static_cast<std::size_t>(start)]) continue;

        ConnectedComponent component;
        component.index = componentIndex++;
        std::queue<int> queue;
        queue.push(start);
        visited[static_cast<std::size_t>(start)] = true;

        while (!queue.empty()) {
            int current = queue.front();
            queue.pop();
            const auto& entity = model.entities[static_cast<std::size_t>(current)];
            component.entityIds.push_back(entity.id);
            if (!containsRigidSet(component.rigidSetIds, entity.rigidSetId)) {
                component.rigidSetIds.push_back(entity.rigidSetId);
            }
            for (int next : adjacency[static_cast<std::size_t>(current)]) {
                if (!visited[static_cast<std::size_t>(next)]) {
                    visited[static_cast<std::size_t>(next)] = true;
                    queue.push(next);
                }
            }
        }

        for (const auto& constraint : model.constraints) {
            bool touchesComponent = false;
            for (EntityId entityId : constraint.entityIds) {
                if (componentContains(component, entityId)) {
                    touchesComponent = true;
                    break;
                }
            }
            if (touchesComponent && !containsConstraint(component.constraintIds, constraint.id)) {
                component.constraintIds.push_back(constraint.id);
            }
        }

        indices.connectedComponents.push_back(component);
    }

    return indices;
}

}
