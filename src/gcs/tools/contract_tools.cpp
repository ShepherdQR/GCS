module;

module gcs.contract_tools;

import gcs.kernel;

namespace gcs::tools {

ModelSnapshot makeTwoPointDistanceModel() {
    ModelSnapshot model;
    model.rigidSets.push_back(RigidSet{RigidSetId{0}, {EntityId{0}}});
    model.rigidSets.push_back(RigidSet{RigidSetId{1}, {EntityId{1}}});

    GeometricEntity first;
    first.id = EntityId{0};
    first.kind = GeometryKind::Point;
    first.rigidSetId = RigidSetId{0};
    first.parameters.dimension = geometryDof(first.kind);
    first.parameters.values[0] = 0.0;
    first.parameters.values[1] = 0.0;
    first.parameters.values[2] = 0.0;

    GeometricEntity second;
    second.id = EntityId{1};
    second.kind = GeometryKind::Point;
    second.rigidSetId = RigidSetId{1};
    second.parameters.dimension = geometryDof(second.kind);
    second.parameters.values[0] = 1.0;
    second.parameters.values[1] = 0.0;
    second.parameters.values[2] = 0.0;

    model.entities.push_back(first);
    model.entities.push_back(second);

    ConstraintInstance distance;
    distance.id = ConstraintId{0};
    distance.kind = ConstraintKind::Distance;
    distance.entityIds = {EntityId{0}, EntityId{1}};
    distance.value = 1.0;
    model.constraints.push_back(distance);
    return model;
}

ContextSnapshot makeWholeContextFor(const ModelSnapshot& model) {
    return makeWholeModelContext(model);
}

}
