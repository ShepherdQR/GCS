module;

#include <vector>

export module gcs.incidence_graph;

export import gcs.kernel;

export namespace gcs::graph {

struct IncidenceInput {
    ModelSnapshot model;
};

struct EntityIncidence {
    EntityId entityId;
    std::vector<ConstraintId> constraintIds;
};

struct ConnectedComponent {
    int index = 0;
    std::vector<EntityId> entityIds;
    std::vector<ConstraintId> constraintIds;
    std::vector<RigidSetId> rigidSetIds;
};

struct IncidenceIndices {
    std::vector<EntityIncidence> entityIncidence;
    std::vector<ConnectedComponent> connectedComponents;
    StageReport report;
};

IncidenceIndices buildIncidenceIndices(const IncidenceInput& input);

}
