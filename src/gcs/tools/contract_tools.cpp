module;

module gcs.contract_tools;

import gcs.kernel;

namespace gcs::tools {

namespace kernel = gcs::kernel;

ModelSnapshot make_two_point_distance_model() {
    ModelSnapshot model;
    model.rigid_sets.push_back(
        kernel::RigidSetDraft{kernel::RigidSetId{0}, {kernel::EntityId{0}}});
    model.rigid_sets.push_back(
        kernel::RigidSetDraft{kernel::RigidSetId{1}, {kernel::EntityId{1}}});

    kernel::EntityDraft first;
    first.id = kernel::EntityId{0};
    first.kind = kernel::GeometryKind::point;
    first.rigid_set_id = kernel::RigidSetId{0};
    first.parameters.dimension = kernel::geometry_dof(first.kind);
    first.parameters.values[0] = 0.0;
    first.parameters.values[1] = 0.0;
    first.parameters.values[2] = 0.0;

    kernel::EntityDraft second;
    second.id = kernel::EntityId{1};
    second.kind = kernel::GeometryKind::point;
    second.rigid_set_id = kernel::RigidSetId{1};
    second.parameters.dimension = kernel::geometry_dof(second.kind);
    second.parameters.values[0] = 1.0;
    second.parameters.values[1] = 0.0;
    second.parameters.values[2] = 0.0;

    model.entities.push_back(first);
    model.entities.push_back(second);

    kernel::ConstraintDraft distance;
    distance.id = kernel::ConstraintId{0};
    distance.kind = kernel::ConstraintKind::distance;
    distance.entity_ids = {kernel::EntityId{0}, kernel::EntityId{1}};
    distance.value = 1.0;
    model.constraints.push_back(distance);
    return model;
}

ModelSnapshot make_two_component_distance_model() {
    ModelSnapshot model = make_two_point_distance_model();

    model.rigid_sets.push_back(
        kernel::RigidSetDraft{kernel::RigidSetId{2}, {kernel::EntityId{2}}});
    model.rigid_sets.push_back(
        kernel::RigidSetDraft{kernel::RigidSetId{3}, {kernel::EntityId{3}}});

    kernel::EntityDraft third;
    third.id = kernel::EntityId{2};
    third.kind = kernel::GeometryKind::point;
    third.rigid_set_id = kernel::RigidSetId{2};
    third.parameters.dimension = kernel::geometry_dof(third.kind);
    third.parameters.values[0] = 10.0;

    kernel::EntityDraft fourth;
    fourth.id = kernel::EntityId{3};
    fourth.kind = kernel::GeometryKind::point;
    fourth.rigid_set_id = kernel::RigidSetId{3};
    fourth.parameters.dimension = kernel::geometry_dof(fourth.kind);
    fourth.parameters.values[0] = 11.0;

    model.entities.push_back(third);
    model.entities.push_back(fourth);

    kernel::ConstraintDraft second_distance;
    second_distance.id = kernel::ConstraintId{1};
    second_distance.kind = kernel::ConstraintKind::distance;
    second_distance.entity_ids = {kernel::EntityId{2}, kernel::EntityId{3}};
    second_distance.value = 1.0;
    model.constraints.push_back(second_distance);
    return model;
}

ModelSnapshot make_missing_entity_reference_model() {
    ModelSnapshot model = make_two_point_distance_model();
    model.constraints.push_back(kernel::ConstraintDraft{
        kernel::ConstraintId{7},
        kernel::ConstraintKind::distance,
        {kernel::EntityId{0}, kernel::EntityId{999}},
        1.0});
    return model;
}

ContextSnapshot make_whole_context_for(const ModelSnapshot& model) {
    return kernel::make_whole_model_context(model);
}

}
