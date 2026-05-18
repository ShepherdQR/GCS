#include "test_framework.h"
#include "core/core.h"

using namespace gcs;

void test_core_enum_geometry_values() {
    GCS_ASSERT_EQ(static_cast<int>(GeometryType::Point), 0, "C01: GeometryType::Point == 0");
    GCS_ASSERT_EQ(static_cast<int>(GeometryType::Line), 1, "C01: GeometryType::Line == 1");
    GCS_ASSERT_EQ(static_cast<int>(GeometryType::Plane), 2, "C01: GeometryType::Plane == 2");
}

void test_core_enum_constraint_values() {
    GCS_ASSERT_EQ(static_cast<int>(ConstraintType::Coincident), 0, "C02: ConstraintType::Coincident == 0");
    GCS_ASSERT_EQ(static_cast<int>(ConstraintType::Parallel), 1, "C02: ConstraintType::Parallel == 1");
    GCS_ASSERT_EQ(static_cast<int>(ConstraintType::Perpendicular), 2, "C02: ConstraintType::Perpendicular == 2");
    GCS_ASSERT_EQ(static_cast<int>(ConstraintType::Distance), 3, "C02: ConstraintType::Distance == 3");
    GCS_ASSERT_EQ(static_cast<int>(ConstraintType::Angle), 4, "C02: ConstraintType::Angle == 4");
}

void test_core_enum_solve_mode_values() {
    GCS_ASSERT_EQ(static_cast<int>(SolveMode::Update), 0, "C02b: SolveMode::Update == 0");
    GCS_ASSERT_EQ(static_cast<int>(SolveMode::Drag), 1, "C02b: SolveMode::Drag == 1");
    GCS_ASSERT_EQ(static_cast<int>(SolveMode::Simulation), 2, "C02b: SolveMode::Simulation == 2");
}

void test_core_geometry_create_point() {
    Geometry g;
    g.id = 10;
    g.type = GeometryType::Point;
    g.rigidSetId = 1;
    for (int i = 0; i < 6; ++i) g.v[i] = 0.0;
    GCS_ASSERT_EQ(g.id, 10, "C03: Geometry id");
    GCS_ASSERT_EQ(g.type, GeometryType::Point, "C03: Geometry type Point");
    GCS_ASSERT_EQ(g.rigidSetId, 1, "C03: Geometry rigidSetId");
}

void test_core_geometry_create_line() {
    Geometry g;
    g.id = 20;
    g.type = GeometryType::Line;
    g.rigidSetId = 2;
    for (int i = 0; i < 6; ++i) g.v[i] = 0.0;
    GCS_ASSERT_EQ(g.id, 20, "C04: Geometry id");
    GCS_ASSERT_EQ(g.type, GeometryType::Line, "C04: Geometry type Line");
    GCS_ASSERT_EQ(g.rigidSetId, 2, "C04: Geometry rigidSetId");
}

void test_core_geometry_create_plane() {
    Geometry g;
    g.id = 30;
    g.type = GeometryType::Plane;
    g.rigidSetId = 3;
    for (int i = 0; i < 6; ++i) g.v[i] = 0.0;
    GCS_ASSERT_EQ(g.id, 30, "C05: Geometry id");
    GCS_ASSERT_EQ(g.type, GeometryType::Plane, "C05: Geometry type Plane");
    GCS_ASSERT_EQ(g.rigidSetId, 3, "C05: Geometry rigidSetId");
}

void test_core_constraint_create() {
    Constraint c;
    c.id = 5;
    c.type = ConstraintType::Distance;
    c.geometryIds = {0, 1};
    c.value = 3.5;
    GCS_ASSERT_EQ(c.id, 5, "C06: Constraint id");
    GCS_ASSERT_EQ(c.type, ConstraintType::Distance, "C06: Constraint type Distance");
    GCS_ASSERT_EQ(c.geometryIds.size(), size_t(2), "C06: Constraint geometryIds size");
    GCS_ASSERT_NEAR(c.value, 3.5, 1e-12, "C06: Constraint value");
}

void test_core_rigidset_create() {
    RigidSet rs;
    rs.id = 7;
    rs.geometryIds = {0, 1, 2};
    GCS_ASSERT_EQ(rs.id, 7, "C07: RigidSet id");
    GCS_ASSERT_EQ(rs.geometryIds.size(), size_t(3), "C07: RigidSet geometryIds size");
}

void test_core_manager_empty() {
    Manager m;
    GCS_ASSERT_EQ(m.rigidSets.size(), size_t(0), "C08: Empty Manager rigidSets");
    GCS_ASSERT_EQ(m.geometries.size(), size_t(0), "C08: Empty Manager geometries");
    GCS_ASSERT_EQ(m.constraints.size(), size_t(0), "C08: Empty Manager constraints");
    GCS_ASSERT_EQ(m.behavior.mode, SolveMode::Update, "C08: Empty Manager behavior Update");
}

void test_core_manager_populate() {
    Manager m;
    RigidSet rs0; rs0.id = 0;
    RigidSet rs1; rs1.id = 1;
    m.rigidSets.push_back(rs0);
    m.rigidSets.push_back(rs1);

    Geometry g0; g0.id = 0; g0.type = GeometryType::Point; g0.rigidSetId = 0;
    Geometry g1; g1.id = 1; g1.type = GeometryType::Line; g1.rigidSetId = 0;
    Geometry g2; g2.id = 2; g2.type = GeometryType::Plane; g2.rigidSetId = 1;
    m.geometries.push_back(g0);
    m.geometries.push_back(g1);
    m.geometries.push_back(g2);

    Constraint c0; c0.id = 0; c0.type = ConstraintType::Distance;
    m.constraints.push_back(c0);

    GCS_ASSERT_EQ(m.rigidSets.size(), size_t(2), "C09: Manager rigidSets size");
    GCS_ASSERT_EQ(m.geometries.size(), size_t(3), "C09: Manager geometries size");
    GCS_ASSERT_EQ(m.constraints.size(), size_t(1), "C09: Manager constraints size");
}

void test_core_manager_find_geometry() {
    Manager m;
    Geometry g0; g0.id = 0; g0.type = GeometryType::Point; g0.rigidSetId = 0;
    Geometry g1; g1.id = 1; g1.type = GeometryType::Line; g1.rigidSetId = 0;
    Geometry g2; g2.id = 2; g2.type = GeometryType::Plane; g2.rigidSetId = 0;
    m.geometries.push_back(g0);
    m.geometries.push_back(g1);
    m.geometries.push_back(g2);

    auto* found = m.findGeometry(1);
    GCS_ASSERT_NE(found, nullptr, "C10: findGeometry(1) not null");
    if (found) GCS_ASSERT_EQ(found->id, 1, "C10: findGeometry(1) id");
}

void test_core_manager_find_geometry_missing() {
    Manager m;
    Geometry g0; g0.id = 0; g0.type = GeometryType::Point; g0.rigidSetId = 0;
    Geometry g1; g1.id = 1; g0.type = GeometryType::Point; g1.rigidSetId = 0;
    m.geometries.push_back(g0);
    m.geometries.push_back(g1);

    auto* found = m.findGeometry(99);
    GCS_ASSERT_EQ(found, nullptr, "C11: findGeometry(99) null");
}

void test_core_manager_find_constraint() {
    Manager m;
    Constraint c0; c0.id = 0; c0.type = ConstraintType::Distance;
    Constraint c1; c1.id = 1; c1.type = ConstraintType::Angle;
    m.constraints.push_back(c0);
    m.constraints.push_back(c1);

    auto* found = m.findConstraint(0);
    GCS_ASSERT_NE(found, nullptr, "C12: findConstraint(0) not null");
    if (found) GCS_ASSERT_EQ(found->id, 0, "C12: findConstraint(0) id");
}

void test_core_manager_find_rigidset() {
    Manager m;
    RigidSet rs0; rs0.id = 0;
    RigidSet rs1; rs1.id = 1;
    m.rigidSets.push_back(rs0);
    m.rigidSets.push_back(rs1);

    auto* found = m.findRigidSet(1);
    GCS_ASSERT_NE(found, nullptr, "C13: findRigidSet(1) not null");
    if (found) GCS_ASSERT_EQ(found->id, 1, "C13: findRigidSet(1) id");
}

void test_core_helper_typename_geometry() {
    GCS_ASSERT_EQ(typeNameGeometry(GeometryType::Point), std::string("Point"), "C14: typeNameGeometry Point");
    GCS_ASSERT_EQ(typeNameGeometry(GeometryType::Line), std::string("Line"), "C14: typeNameGeometry Line");
    GCS_ASSERT_EQ(typeNameGeometry(GeometryType::Plane), std::string("Plane"), "C14: typeNameGeometry Plane");
}

void test_core_helper_typename_constraint() {
    GCS_ASSERT_EQ(typeNameConstraint(ConstraintType::Coincident), std::string("Coincident"), "C15: typeNameConstraint Coincident");
    GCS_ASSERT_EQ(typeNameConstraint(ConstraintType::Parallel), std::string("Parallel"), "C15: typeNameConstraint Parallel");
    GCS_ASSERT_EQ(typeNameConstraint(ConstraintType::Perpendicular), std::string("Perpendicular"), "C15: typeNameConstraint Perpendicular");
    GCS_ASSERT_EQ(typeNameConstraint(ConstraintType::Distance), std::string("Distance"), "C15: typeNameConstraint Distance");
    GCS_ASSERT_EQ(typeNameConstraint(ConstraintType::Angle), std::string("Angle"), "C15: typeNameConstraint Angle");
}

void test_core_helper_typename_solve_mode() {
    GCS_ASSERT_EQ(typeNameSolveMode(SolveMode::Update), std::string("Update"), "C15b: typeNameSolveMode Update");
    GCS_ASSERT_EQ(typeNameSolveMode(SolveMode::Drag), std::string("Drag"), "C15b: typeNameSolveMode Drag");
    GCS_ASSERT_EQ(typeNameSolveMode(SolveMode::Simulation), std::string("Simulation"), "C15b: typeNameSolveMode Simulation");
}

void test_core_helper_dof_geometry() {
    GCS_ASSERT_EQ(dofGeometry(GeometryType::Point), 3, "C16: dofGeometry Point = 3");
    GCS_ASSERT_EQ(dofGeometry(GeometryType::Line), 6, "C16: dofGeometry Line = 6");
    GCS_ASSERT_EQ(dofGeometry(GeometryType::Plane), 6, "C16: dofGeometry Plane = 6");
}

void test_core_helper_dof_removed_constraint() {
    GCS_ASSERT_EQ(dofRemovedConstraint(ConstraintType::Coincident), 3, "C17: dofRemovedConstraint Coincident = 3");
    GCS_ASSERT_EQ(dofRemovedConstraint(ConstraintType::Parallel), 2, "C17: dofRemovedConstraint Parallel = 2");
    GCS_ASSERT_EQ(dofRemovedConstraint(ConstraintType::Perpendicular), 1, "C17: dofRemovedConstraint Perpendicular = 1");
    GCS_ASSERT_EQ(dofRemovedConstraint(ConstraintType::Distance), 1, "C17: dofRemovedConstraint Distance = 1");
    GCS_ASSERT_EQ(dofRemovedConstraint(ConstraintType::Angle), 1, "C17: dofRemovedConstraint Angle = 1");
}

int main() {
    std::cout << "=== Core Interface Tests ===\n\n";

    test_core_enum_geometry_values();
    test_core_enum_constraint_values();
    test_core_enum_solve_mode_values();
    test_core_geometry_create_point();
    test_core_geometry_create_line();
    test_core_geometry_create_plane();
    test_core_constraint_create();
    test_core_rigidset_create();
    test_core_manager_empty();
    test_core_manager_populate();
    test_core_manager_find_geometry();
    test_core_manager_find_geometry_missing();
    test_core_manager_find_constraint();
    test_core_manager_find_rigidset();
    test_core_helper_typename_geometry();
    test_core_helper_typename_constraint();
    test_core_helper_typename_solve_mode();
    test_core_helper_dof_geometry();
    test_core_helper_dof_removed_constraint();

    GCS_TEST_SUMMARY();
}
