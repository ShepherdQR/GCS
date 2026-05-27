module;

#include <algorithm>
#include <cstddef>
#include <queue>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

module gcs.incidence_graph;

import gcs.kernel;

namespace gcs::graph {

namespace kernel = gcs::kernel;

namespace {

int entity_index(const std::vector<EntityId>& entity_ids, EntityId entity_id) {
    for (int i = 0; i < static_cast<int>(entity_ids.size()); ++i) {
        if (entity_ids[static_cast<std::size_t>(i)] == entity_id) return i;
    }
    return -1;
}

bool component_contains(const ConnectedComponent& component, EntityId entity_id) {
    return kernel::contains_entity(component.entity_ids, entity_id);
}

bool rigid_edge_matches(const RigidBodyEdge& edge,
                        RigidSetId first_rigid_set_id,
                        RigidSetId second_rigid_set_id) {
    return edge.first_rigid_set_id == first_rigid_set_id &&
           edge.second_rigid_set_id == second_rigid_set_id;
}

void append_report(StageReport& target, const StageReport& source) {
    for (const auto& message : source.messages) {
        kernel::append_report_message(target, message);
    }
    if (source.status == kernel::StageStatus::error) {
        target.status = kernel::StageStatus::error;
    } else if (source.status == kernel::StageStatus::warning &&
               target.status == kernel::StageStatus::ok) {
        target.status = kernel::StageStatus::warning;
    }
}

MalformedEdgeReport make_malformed_edge_report(ConstraintId constraint_id,
                                               std::vector<EntityId> missing_entity_ids) {
    return MalformedEdgeReport{
        constraint_id,
        std::move(missing_entity_ids),
        "incidence.missing_entity",
        "Constraint references one or more entities missing from the incidence hypergraph."};
}

void report_malformed_edge(StageReport& report, const MalformedEdgeReport& malformed) {
    std::vector<kernel::StableId> subjects;
    subjects.push_back(kernel::StableId{"constraint", malformed.constraint_id.value});
    for (EntityId entity_id : malformed.missing_entity_ids) {
        subjects.push_back(kernel::StableId{"entity", entity_id.value});
    }
    kernel::append_report_message(
        report,
        kernel::make_report_message(
            kernel::ReportSeverity::error,
            kernel::ReportCode{malformed.code},
            malformed.message,
            std::move(subjects)));
}

std::vector<EntityId> find_missing_entities(const IncidenceHypergraph& hypergraph,
                                            const std::vector<EntityId>& entity_ids) {
    std::vector<EntityId> missing;
    for (EntityId entity_id : entity_ids) {
        if (!kernel::contains_entity(hypergraph.entity_ids, entity_id)) {
            missing.push_back(entity_id);
        }
    }
    return missing;
}

std::vector<int> incident_entity_indexes(const IncidenceHypergraph& hypergraph,
                                         const IncidenceHyperedge& hyperedge) {
    std::vector<int> indexes;
    if (hyperedge.malformed) return indexes;
    for (EntityId entity_id : hyperedge.entity_ids) {
        const int index = entity_index(hypergraph.entity_ids, entity_id);
        if (index >= 0) indexes.push_back(index);
    }
    return indexes;
}

RigidSetId rigid_set_for_entity(const ModelSnapshot& model, EntityId entity_id) {
    if (const auto* entity = kernel::find_entity(model, entity_id)) {
        return entity->rigid_set_id;
    }
    return RigidSetId{};
}

void append_sorted_unique_constraint(std::vector<ConstraintId>& ids, ConstraintId id) {
    if (!kernel::contains_constraint(ids, id)) ids.push_back(id);
}

}  // namespace

gcs::kernel::ContractResult<IncidenceHypergraph> build_hypergraph(
    HypergraphBuildRequest request) {
    kernel::ContractResult<IncidenceHypergraph> result;
    result.report = kernel::make_stage_report("incidence_graph.build_hypergraph");
    result.payload.report = result.report;

    const auto& model = request.model;
    result.payload.entity_ids.reserve(model.entities.size());
    result.payload.constraint_ids.reserve(model.constraints.size());
    result.payload.hyperedges.reserve(model.constraints.size());

    for (const auto& entity : model.entities) {
        result.payload.entity_ids.push_back(entity.id);
    }

    for (const auto& constraint : model.constraints) {
        result.payload.constraint_ids.push_back(constraint.id);

        IncidenceHyperedge hyperedge;
        hyperedge.id = HyperedgeId{static_cast<std::uint64_t>(result.payload.hyperedges.size())};
        hyperedge.constraint_id = constraint.id;
        hyperedge.entity_ids = constraint.entity_ids;
        hyperedge.missing_entity_ids = find_missing_entities(result.payload, constraint.entity_ids);
        hyperedge.malformed = !hyperedge.missing_entity_ids.empty();

        if (hyperedge.malformed) {
            auto malformed = make_malformed_edge_report(
                constraint.id,
                hyperedge.missing_entity_ids);
            report_malformed_edge(result.report, malformed);
            result.payload.malformed_edges.push_back(std::move(malformed));
            if (!request.options.quarantine_malformed_edges) {
                result.payload.hyperedges.push_back(std::move(hyperedge));
                continue;
            }
        }

        result.payload.hyperedges.push_back(std::move(hyperedge));
    }

    result.payload.report = result.report;
    return result;
}

gcs::kernel::ContractResult<IncidenceIndices> build_indices(
    const IncidenceHypergraph& hypergraph) {
    kernel::ContractResult<IncidenceIndices> result;
    result.report = kernel::make_stage_report("incidence_graph.build_indices");
    append_report(result.report, hypergraph.report);

    result.payload.report = result.report;
    result.payload.entity_incidence.reserve(hypergraph.entity_ids.size());
    for (EntityId entity_id : hypergraph.entity_ids) {
        result.payload.entity_incidence.push_back(EntityIncidence{entity_id, {}});
    }

    result.payload.constraint_incidence.reserve(hypergraph.hyperedges.size());
    std::vector<std::vector<int>> adjacency(hypergraph.entity_ids.size());

    for (const auto& hyperedge : hypergraph.hyperedges) {
        result.payload.constraint_incidence.push_back(ConstraintIncidence{
            hyperedge.constraint_id,
            hyperedge.entity_ids,
            !hyperedge.malformed,
            hyperedge.missing_entity_ids});

        const auto indexes = incident_entity_indexes(hypergraph, hyperedge);
        for (int index : indexes) {
            result.payload.entity_incidence[static_cast<std::size_t>(index)]
                .constraint_ids.push_back(hyperedge.constraint_id);
        }

        for (int lhs : indexes) {
            for (int rhs : indexes) {
                if (lhs != rhs) adjacency[static_cast<std::size_t>(lhs)].push_back(rhs);
            }
        }
    }

    std::vector<bool> visited(hypergraph.entity_ids.size(), false);
    int component_index = 0;
    for (int start = 0; start < static_cast<int>(hypergraph.entity_ids.size()); ++start) {
        if (visited[static_cast<std::size_t>(start)]) continue;

        ConnectedComponent component;
        component.index = component_index++;
        std::queue<int> queue;
        queue.push(start);
        visited[static_cast<std::size_t>(start)] = true;

        while (!queue.empty()) {
            int current = queue.front();
            queue.pop();
            component.entity_ids.push_back(hypergraph.entity_ids[static_cast<std::size_t>(current)]);
            for (int next : adjacency[static_cast<std::size_t>(current)]) {
                if (!visited[static_cast<std::size_t>(next)]) {
                    visited[static_cast<std::size_t>(next)] = true;
                    queue.push(next);
                }
            }
        }

        for (const auto& hyperedge : hypergraph.hyperedges) {
            if (hyperedge.malformed) continue;
            bool touches_component = false;
            for (EntityId entity_id : hyperedge.entity_ids) {
                if (component_contains(component, entity_id)) {
                    touches_component = true;
                    break;
                }
            }
            if (touches_component) {
                append_sorted_unique_constraint(
                    component.constraint_ids,
                    hyperedge.constraint_id);
            }
        }

        result.payload.connected_components.push_back(component);
    }

    result.payload.report = result.report;
    return result;
}

gcs::kernel::ContractResult<RigidBodyGraph> build_rigid_body_graph(
    const ModelSnapshot& model,
    const IncidenceHypergraph& hypergraph) {
    kernel::ContractResult<RigidBodyGraph> result;
    result.report = kernel::make_stage_report("incidence_graph.build_rigid_body_graph");
    append_report(result.report, hypergraph.report);

    for (const auto& rigid_set : model.rigid_sets) {
        result.payload.nodes.push_back(RigidBodyNode{rigid_set.id, rigid_set.entity_ids});
    }

    for (const auto& hyperedge : hypergraph.hyperedges) {
        if (hyperedge.malformed) continue;

        std::vector<RigidSetId> rigid_sets;
        for (EntityId entity_id : hyperedge.entity_ids) {
            RigidSetId rigid_set_id = rigid_set_for_entity(model, entity_id);
            if (!kernel::contains_rigid_set(rigid_sets, rigid_set_id)) {
                rigid_sets.push_back(rigid_set_id);
            }
        }

        for (std::size_t i = 0; i < rigid_sets.size(); ++i) {
            for (std::size_t j = i + 1; j < rigid_sets.size(); ++j) {
                RigidSetId first = rigid_sets[i];
                RigidSetId second = rigid_sets[j];
                if (second.value < first.value) {
                    std::swap(first, second);
                }

                auto found = std::find_if(
                    result.payload.edges.begin(),
                    result.payload.edges.end(),
                    [first, second](const RigidBodyEdge& edge) {
                        return rigid_edge_matches(edge, first, second);
                    });
                if (found == result.payload.edges.end()) {
                    RigidBodyEdge edge;
                    edge.id = RigidBodyEdgeId{
                        static_cast<std::uint64_t>(result.payload.edges.size())};
                    edge.first_rigid_set_id = first;
                    edge.second_rigid_set_id = second;
                    edge.constraint_ids.push_back(hyperedge.constraint_id);
                    result.payload.edges.push_back(std::move(edge));
                } else {
                    append_sorted_unique_constraint(found->constraint_ids, hyperedge.constraint_id);
                }
            }
        }
    }

    result.payload.report = result.report;
    return result;
}

gcs::kernel::ContractResult<RigidSetPairGroupingReport> build_rigid_set_pair_groups(
    const ModelSnapshot& model,
    const RigidBodyGraph& rigid_body_graph) {
    kernel::ContractResult<RigidSetPairGroupingReport> result;
    result.report = kernel::make_stage_report("incidence_graph.build_rigid_set_pair_groups");
    append_report(result.report, rigid_body_graph.report);

    for (const auto& edge : rigid_body_graph.edges) {
        RigidSetPairConstraintGroup group;
        group.first_rigid_set_id = edge.first_rigid_set_id;
        group.second_rigid_set_id = edge.second_rigid_set_id;
        group.constraint_ids = edge.constraint_ids;
        result.payload.pair_group_count++;
        result.payload.total_constraints_grouped +=
            static_cast<int>(edge.constraint_ids.size());
    }

    // Count same-rigid-set constraints (constraints whose entities all belong to
    // the same rigid set). These cannot become spanning-tree edges.
    for (const auto& constraint : model.constraints) {
        RigidSetId first_rs{};
        bool first_set = true;
        bool same_rs = true;
        for (EntityId entity_id : constraint.entity_ids) {
            if (const auto* entity = kernel::find_entity(model, entity_id)) {
                if (first_set) {
                    first_rs = entity->rigid_set_id;
                    first_set = false;
                } else if (!(entity->rigid_set_id == first_rs)) {
                    same_rs = false;
                    break;
                }
            }
        }
        if (same_rs && !first_set) {
            result.payload.same_rigid_set_constraint_count++;
        }
    }

    result.payload.report = result.report;
    return result;
}

gcs::kernel::ContractResult<GraphDump> dump_graph(const IncidenceHypergraph& hypergraph,
                                                  GraphDumpRequest request) {
    kernel::ContractResult<GraphDump> result;
    result.report = kernel::make_stage_report("incidence_graph.dump_graph");

    std::ostringstream output;
    output << "entities";
    for (EntityId entity_id : hypergraph.entity_ids) {
        output << " " << entity_id.value;
    }
    output << "\nconstraints";
    for (ConstraintId constraint_id : hypergraph.constraint_ids) {
        output << " " << constraint_id.value;
    }
    output << "\nhyperedges\n";
    for (const auto& hyperedge : hypergraph.hyperedges) {
        output << hyperedge.id.value << " c=" << hyperedge.constraint_id.value
               << " entities=";
        for (std::size_t i = 0; i < hyperedge.entity_ids.size(); ++i) {
            if (i > 0) output << ",";
            output << hyperedge.entity_ids[i].value;
        }
        output << " malformed=" << (hyperedge.malformed ? "true" : "false") << "\n";
    }

    if (request.include_malformed_edges) {
        output << "malformed\n";
        for (const auto& malformed : hypergraph.malformed_edges) {
            output << "c=" << malformed.constraint_id.value << " missing=";
            for (std::size_t i = 0; i < malformed.missing_entity_ids.size(); ++i) {
                if (i > 0) output << ",";
                output << malformed.missing_entity_ids[i].value;
            }
            output << " code=" << malformed.code << "\n";
        }
    }

    result.payload.canonical_text = output.str();
    result.payload.hyperedge_count = static_cast<int>(hypergraph.hyperedges.size());
    result.payload.malformed_edge_count =
        static_cast<int>(hypergraph.malformed_edges.size());
    return result;
}

IncidenceIndices build_incidence_indices(const IncidenceInput& input) {
    auto hypergraph = build_hypergraph(HypergraphBuildRequest{input.model, {}});
    auto indices = build_indices(hypergraph.payload);

    for (auto& component : indices.payload.connected_components) {
        for (EntityId entity_id : component.entity_ids) {
            const auto* entity = kernel::find_entity(input.model, entity_id);
            if (entity != nullptr &&
                !kernel::contains_rigid_set(component.rigid_set_ids, entity->rigid_set_id)) {
                component.rigid_set_ids.push_back(entity->rigid_set_id);
            }
        }
    }
    indices.payload.report = indices.report;
    return indices.payload;
}

}
