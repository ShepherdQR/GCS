module;

#include <vector>

export module gcs.incidence_graph;

export import gcs.kernel;

export namespace gcs::graph {

using gcs::kernel::ConstraintId;
using gcs::kernel::EntityId;
using gcs::kernel::ModelSnapshot;
using gcs::kernel::RigidSetId;
using gcs::kernel::StageReport;

struct IncidenceInput {
    ModelSnapshot model;
};

struct EntityIncidence {
    EntityId entity_id;
    std::vector<ConstraintId> constraint_ids;
};

struct ConnectedComponent {
    int index = 0;
    std::vector<EntityId> entity_ids;
    std::vector<ConstraintId> constraint_ids;
    std::vector<RigidSetId> rigid_set_ids;
};

struct IncidenceIndices {
    std::vector<EntityIncidence> entity_incidence;
    std::vector<ConnectedComponent> connected_components;
    StageReport report;
};

IncidenceIndices build_incidence_indices(const IncidenceInput& input);

}
