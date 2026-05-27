module;

#include <cstdint>
#include <string>
#include <vector>

export module gcs.incidence_graph;

export import gcs.kernel;

export namespace gcs::graph {

using gcs::kernel::ConstraintId;
using gcs::kernel::EntityId;
using gcs::kernel::ModelSnapshot;
using gcs::kernel::RigidSetId;
using gcs::kernel::StageReport;

struct HyperedgeId {
    std::uint64_t value = 0;
    friend bool operator==(HyperedgeId, HyperedgeId) = default;
};

struct RigidBodyEdgeId {
    std::uint64_t value = 0;
    friend bool operator==(RigidBodyEdgeId, RigidBodyEdgeId) = default;
};

struct HypergraphBuildOptions {
    bool quarantine_malformed_edges = true;
};

struct HypergraphBuildRequest {
    ModelSnapshot model;
    HypergraphBuildOptions options;
};

struct IncidenceInput {
    ModelSnapshot model;
};

struct MalformedEdgeReport {
    ConstraintId constraint_id;
    std::vector<EntityId> missing_entity_ids;
    std::string code;
    std::string message;
};

struct IncidenceHyperedge {
    HyperedgeId id;
    ConstraintId constraint_id;
    std::vector<EntityId> entity_ids;
    bool malformed = false;
    std::vector<EntityId> missing_entity_ids;
};

struct IncidenceHypergraph {
    std::vector<EntityId> entity_ids;
    std::vector<ConstraintId> constraint_ids;
    std::vector<IncidenceHyperedge> hyperedges;
    std::vector<MalformedEdgeReport> malformed_edges;
    StageReport report;
};

struct EntityIncidence {
    EntityId entity_id;
    std::vector<ConstraintId> constraint_ids;
};

struct ConstraintIncidence {
    ConstraintId constraint_id;
    std::vector<EntityId> entity_ids;
    bool valid = true;
    std::vector<EntityId> missing_entity_ids;
};

struct ConnectedComponent {
    int index = 0;
    std::vector<EntityId> entity_ids;
    std::vector<ConstraintId> constraint_ids;
    std::vector<RigidSetId> rigid_set_ids;
};

struct IncidenceIndices {
    std::vector<EntityIncidence> entity_incidence;
    std::vector<ConstraintIncidence> constraint_incidence;
    std::vector<ConnectedComponent> connected_components;
    StageReport report;
};

struct RigidBodyNode {
    RigidSetId rigid_set_id;
    std::vector<EntityId> entity_ids;
};

struct RigidBodyEdge {
    RigidBodyEdgeId id;
    RigidSetId first_rigid_set_id;
    RigidSetId second_rigid_set_id;
    std::vector<ConstraintId> constraint_ids;
};

struct RigidBodyGraph {
    std::vector<RigidBodyNode> nodes;
    std::vector<RigidBodyEdge> edges;
    StageReport report;
};

// --- Spanning tree support ---

struct RigidSetPairConstraintGroup {
    RigidSetId first_rigid_set_id;
    RigidSetId second_rigid_set_id;
    std::vector<ConstraintId> constraint_ids;
};

struct RigidSetPairGroupingReport {
    int pair_group_count = 0;
    int total_constraints_grouped = 0;
    int same_rigid_set_constraint_count = 0;
    StageReport report;
};

struct GraphDumpRequest {
    bool include_malformed_edges = true;
};

struct GraphDump {
    std::string canonical_text;
    int hyperedge_count = 0;
    int malformed_edge_count = 0;
};

gcs::kernel::ContractResult<IncidenceHypergraph> build_hypergraph(
    HypergraphBuildRequest request);
gcs::kernel::ContractResult<IncidenceIndices> build_indices(
    const IncidenceHypergraph& hypergraph);
gcs::kernel::ContractResult<RigidBodyGraph> build_rigid_body_graph(
    const ModelSnapshot& model,
    const IncidenceHypergraph& hypergraph);
gcs::kernel::ContractResult<RigidSetPairGroupingReport> build_rigid_set_pair_groups(
    const ModelSnapshot& model,
    const RigidBodyGraph& rigid_body_graph);
gcs::kernel::ContractResult<GraphDump> dump_graph(const IncidenceHypergraph& hypergraph,
                                                  GraphDumpRequest request = {});

IncidenceIndices build_incidence_indices(const IncidenceInput& input);

}
