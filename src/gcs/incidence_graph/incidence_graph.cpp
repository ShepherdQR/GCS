module;

#include <cstddef>
#include <queue>
#include <utility>
#include <vector>

module gcs.incidence_graph;

import gcs.kernel;

namespace gcs::graph {

namespace kernel = gcs::kernel;

namespace {

int entity_index(const ModelSnapshot& model, EntityId entity_id) {
    for (int i = 0; i < static_cast<int>(model.entities.size()); ++i) {
        if (model.entities[static_cast<std::size_t>(i)].id == entity_id) return i;
    }
    return -1;
}

bool component_contains(const ConnectedComponent& component, EntityId entity_id) {
    return kernel::contains_entity(component.entity_ids, entity_id);
}

}  // namespace

IncidenceIndices build_incidence_indices(const IncidenceInput& input) {
    IncidenceIndices indices;
    indices.report = kernel::make_stage_report("incidence_graph.build_indices");

    const auto& model = input.model;
    indices.entity_incidence.reserve(model.entities.size());
    for (const auto& entity : model.entities) {
        indices.entity_incidence.push_back(EntityIncidence{entity.id, {}});
    }

    std::vector<std::vector<int>> adjacency(model.entities.size());
    for (const auto& constraint : model.constraints) {
        std::vector<int> incident_entity_indexes;
        for (EntityId entity_id : constraint.entity_ids) {
            int index = entity_index(model, entity_id);
            if (index < 0) {
                kernel::append_report_message(
                    indices.report,
                    kernel::make_report_message(
                        kernel::ReportSeverity::error,
                        kernel::ReportCode{"incidence.missing_entity"},
                        "Constraint references an entity missing from incidence indices.",
                        {kernel::StableId{"constraint", constraint.id.value},
                         kernel::StableId{"entity", entity_id.value}}));
                continue;
            }
            indices.entity_incidence[static_cast<std::size_t>(index)].constraint_ids.push_back(
                constraint.id);
            incident_entity_indexes.push_back(index);
        }

        for (int lhs : incident_entity_indexes) {
            for (int rhs : incident_entity_indexes) {
                if (lhs != rhs) adjacency[static_cast<std::size_t>(lhs)].push_back(rhs);
            }
        }
    }

    std::vector<bool> visited(model.entities.size(), false);
    int component_index = 0;
    for (int start = 0; start < static_cast<int>(model.entities.size()); ++start) {
        if (visited[static_cast<std::size_t>(start)]) continue;

        ConnectedComponent component;
        component.index = component_index++;
        std::queue<int> queue;
        queue.push(start);
        visited[static_cast<std::size_t>(start)] = true;

        while (!queue.empty()) {
            int current = queue.front();
            queue.pop();
            const auto& entity = model.entities[static_cast<std::size_t>(current)];
            component.entity_ids.push_back(entity.id);
            if (!kernel::contains_rigid_set(component.rigid_set_ids, entity.rigid_set_id)) {
                component.rigid_set_ids.push_back(entity.rigid_set_id);
            }
            for (int next : adjacency[static_cast<std::size_t>(current)]) {
                if (!visited[static_cast<std::size_t>(next)]) {
                    visited[static_cast<std::size_t>(next)] = true;
                    queue.push(next);
                }
            }
        }

        for (const auto& constraint : model.constraints) {
            bool touches_component = false;
            for (EntityId entity_id : constraint.entity_ids) {
                if (component_contains(component, entity_id)) {
                    touches_component = true;
                    break;
                }
            }
            if (touches_component &&
                !kernel::contains_constraint(component.constraint_ids, constraint.id)) {
                component.constraint_ids.push_back(constraint.id);
            }
        }

        indices.connected_components.push_back(component);
    }

    return indices;
}

}
