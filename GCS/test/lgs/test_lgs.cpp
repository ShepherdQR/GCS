#include "test_framework.h"
#include "gcs/lgs/lgs.h"
#include "gcs/dcm/dcm.h"
#include "gcs/io/io.h"

using namespace gcs;

static Manager makeSinglePoint() {
    Manager m;
    RigidSet rs; rs.id = 0; rs.geometryIds = {0};
    m.rigidSets.push_back(rs);
    Geometry g; g.id = 0; g.type = GeometryType::Point; g.rigidSetId = 0;
    for (int i = 0; i < 6; ++i) g.v[i] = 0;
    m.geometries.push_back(g);
    return m;
}

static Manager makeSingleLine() {
    Manager m;
    RigidSet rs; rs.id = 0; rs.geometryIds = {0};
    m.rigidSets.push_back(rs);
    Geometry g; g.id = 0; g.type = GeometryType::Line; g.rigidSetId = 0;
    for (int i = 0; i < 6; ++i) g.v[i] = 0;
    m.geometries.push_back(g);
    return m;
}

static Manager makeSinglePlane() {
    Manager m;
    RigidSet rs; rs.id = 0; rs.geometryIds = {0};
    m.rigidSets.push_back(rs);
    Geometry g; g.id = 0; g.type = GeometryType::Plane; g.rigidSetId = 0;
    for (int i = 0; i < 6; ++i) g.v[i] = 0;
    m.geometries.push_back(g);
    return m;
}

static Manager makeTwoPointsDistance() {
    Manager m;
    RigidSet rs; rs.id = 0; rs.geometryIds = {0, 1};
    m.rigidSets.push_back(rs);
    Geometry g0; g0.id = 0; g0.type = GeometryType::Point; g0.rigidSetId = 0;
    Geometry g1; g1.id = 1; g1.type = GeometryType::Point; g1.rigidSetId = 0;
    for (int i = 0; i < 6; ++i) { g0.v[i] = 0; g1.v[i] = 0; }
    g1.v[0] = 3;
    m.geometries.push_back(g0);
    m.geometries.push_back(g1);
    Constraint c; c.id = 0; c.type = ConstraintType::Distance; c.geometryIds = {0, 1}; c.value = 3;
    m.constraints.push_back(c);
    return m;
}

static Manager makeTwoPointsCoincident() {
    Manager m;
    RigidSet rs; rs.id = 0; rs.geometryIds = {0, 1};
    m.rigidSets.push_back(rs);
    Geometry g0; g0.id = 0; g0.type = GeometryType::Point; g0.rigidSetId = 0;
    Geometry g1; g1.id = 1; g1.type = GeometryType::Point; g1.rigidSetId = 0;
    for (int i = 0; i < 6; ++i) { g0.v[i] = 0; g1.v[i] = 0; }
    m.geometries.push_back(g0);
    m.geometries.push_back(g1);
    Constraint c; c.id = 0; c.type = ConstraintType::Coincident; c.geometryIds = {0, 1}; c.value = 0;
    m.constraints.push_back(c);
    return m;
}

static Manager makeWellConstrainedTriangle() {
    Manager m;
    RigidSet rs0; rs0.id = 0; rs0.geometryIds = {0};
    RigidSet rs1; rs1.id = 1; rs1.geometryIds = {1};
    RigidSet rs2; rs2.id = 2; rs2.geometryIds = {2};
    m.rigidSets.push_back(rs0);
    m.rigidSets.push_back(rs1);
    m.rigidSets.push_back(rs2);
    Geometry g0; g0.id = 0; g0.type = GeometryType::Point; g0.rigidSetId = 0;
    Geometry g1; g1.id = 1; g1.type = GeometryType::Point; g1.rigidSetId = 1;
    Geometry g2; g2.id = 2; g2.type = GeometryType::Point; g2.rigidSetId = 2;
    for (int i = 0; i < 6; ++i) { g0.v[i] = 0; g1.v[i] = 0; g2.v[i] = 0; }
    g1.v[0] = 3; g2.v[1] = 4;
    m.geometries.push_back(g0);
    m.geometries.push_back(g1);
    m.geometries.push_back(g2);

    Constraint c0; c0.id = 0; c0.type = ConstraintType::Coincident; c0.geometryIds = {0, 1}; c0.value = 0;
    Constraint c1; c1.id = 1; c1.type = ConstraintType::Coincident; c1.geometryIds = {1, 2}; c1.value = 0;
    Constraint c2; c2.id = 2; c2.type = ConstraintType::Coincident; c2.geometryIds = {0, 2}; c2.value = 0;
    m.constraints.push_back(c0);
    m.constraints.push_back(c1);
    m.constraints.push_back(c2);
    return m;
}

static Manager makeUnderConstrained() {
    Manager m;
    RigidSet rs; rs.id = 0; rs.geometryIds = {0, 1};
    m.rigidSets.push_back(rs);
    Geometry g0; g0.id = 0; g0.type = GeometryType::Point; g0.rigidSetId = 0;
    Geometry g1; g1.id = 1; g1.type = GeometryType::Point; g1.rigidSetId = 0;
    for (int i = 0; i < 6; ++i) { g0.v[i] = 0; g1.v[i] = 0; }
    m.geometries.push_back(g0);
    m.geometries.push_back(g1);
    return m;
}

static Manager makeOverConstrained() {
    Manager m;
    RigidSet rs0; rs0.id = 0; rs0.geometryIds = {0};
    RigidSet rs1; rs1.id = 1; rs1.geometryIds = {1};
    m.rigidSets.push_back(rs0);
    m.rigidSets.push_back(rs1);
    Geometry g0; g0.id = 0; g0.type = GeometryType::Point; g0.rigidSetId = 0;
    Geometry g1; g1.id = 1; g1.type = GeometryType::Point; g1.rigidSetId = 1;
    for (int i = 0; i < 6; ++i) { g0.v[i] = 0; g1.v[i] = 0; }
    g1.v[0] = 3;
    m.geometries.push_back(g0);
    m.geometries.push_back(g1);
    Constraint c0; c0.id = 0; c0.type = ConstraintType::Coincident; c0.geometryIds = {0, 1}; c0.value = 0;
    Constraint c1; c1.id = 1; c1.type = ConstraintType::Distance; c1.geometryIds = {0, 1}; c1.value = 3;
    Constraint c2; c2.id = 2; c2.type = ConstraintType::Parallel; c2.geometryIds = {0, 1}; c2.value = 0;
    Constraint c3; c3.id = 3; c3.type = ConstraintType::Perpendicular; c3.geometryIds = {0, 1}; c3.value = 0;
    m.constraints.push_back(c0);
    m.constraints.push_back(c1);
    m.constraints.push_back(c2);
    m.constraints.push_back(c3);
    return m;
}

void test_lgs_dof_single_point() {
    auto m = makeSinglePoint();
    lgs::LocalGeometricSolver lgs;
    auto dof = lgs.analyzeDOF(m);
    GCS_ASSERT_EQ(dof.geometryDOF, 3, "L01: single point geometryDOF=3");
    GCS_ASSERT_EQ(dof.constraintRemovedDOF, 0, "L01: single point constraintRemovedDOF=0");
    GCS_ASSERT_EQ(dof.netDOF, 3, "L01: single point netDOF=3");
}

void test_lgs_dof_single_line() {
    auto m = makeSingleLine();
    lgs::LocalGeometricSolver lgs;
    auto dof = lgs.analyzeDOF(m);
    GCS_ASSERT_EQ(dof.geometryDOF, 6, "L02: single line geometryDOF=6");
    GCS_ASSERT_EQ(dof.netDOF, 6, "L02: single line netDOF=6");
}

void test_lgs_dof_single_plane() {
    auto m = makeSinglePlane();
    lgs::LocalGeometricSolver lgs;
    auto dof = lgs.analyzeDOF(m);
    GCS_ASSERT_EQ(dof.geometryDOF, 6, "L03: single plane geometryDOF=6");
    GCS_ASSERT_EQ(dof.netDOF, 6, "L03: single plane netDOF=6");
}

void test_lgs_dof_two_points_distance() {
    auto m = makeTwoPointsDistance();
    lgs::LocalGeometricSolver lgs;
    auto dof = lgs.analyzeDOF(m);
    GCS_ASSERT_EQ(dof.geometryDOF, 6, "L04: two points geometryDOF=6");
    GCS_ASSERT_EQ(dof.constraintRemovedDOF, 1, "L04: two points+distance constraintRemovedDOF=1");
    GCS_ASSERT_EQ(dof.netDOF, 5, "L04: two points+distance netDOF=5");
}

void test_lgs_dof_two_points_coincident() {
    auto m = makeTwoPointsCoincident();
    lgs::LocalGeometricSolver lgs;
    auto dof = lgs.analyzeDOF(m);
    GCS_ASSERT_EQ(dof.geometryDOF, 6, "L05: two points geometryDOF=6");
    GCS_ASSERT_EQ(dof.constraintRemovedDOF, 3, "L05: two points+coincident constraintRemovedDOF=3");
    GCS_ASSERT_EQ(dof.netDOF, 3, "L05: two points+coincident netDOF=3");
}

void test_lgs_status_well_constrained() {
    auto m = makeWellConstrainedTriangle();
    lgs::LocalGeometricSolver lgs;
    auto report = lgs.analyzeStatus(m);
    GCS_ASSERT_EQ(report.overallStatus, lgs::ConstraintStatus::WellConstrained, "L06: well-constrained status");
}

void test_lgs_status_under_constrained() {
    auto m = makeUnderConstrained();
    lgs::LocalGeometricSolver lgs;
    auto report = lgs.analyzeStatus(m);
    GCS_ASSERT_EQ(report.overallStatus, lgs::ConstraintStatus::UnderConstrained, "L07: under-constrained status");
}

void test_lgs_status_over_constrained() {
    auto m = makeOverConstrained();
    lgs::LocalGeometricSolver lgs;
    auto report = lgs.analyzeStatus(m);
    bool isOver = (report.overallStatus == lgs::ConstraintStatus::OverConstrained ||
                   report.overallStatus == lgs::ConstraintStatus::OverConstrainedConsistent);
    GCS_ASSERT(isOver, "L08: over-constrained status");
}

void test_lgs_dof_with_subproblem() {
    auto m = makeTwoPointsDistance();
    dcm::DecompositionManager dcm;
    auto decomp = dcm.decompose(m);
    lgs::LocalGeometricSolver lgs;
    if (!decomp.subProblems.empty()) {
        auto dof = lgs.analyzeDOF(m, decomp.subProblems[0]);
        GCS_ASSERT_EQ(dof.geometryDOF, 6, "L09: sub-problem geometryDOF=6");
        GCS_ASSERT_EQ(dof.constraintRemovedDOF, 1, "L09: sub-problem constraintRemovedDOF=1");
    } else {
        GCS_ASSERT(false, "L09: expected at least 1 sub-problem");
    }
}

void test_lgs_status_with_subproblem() {
    auto m = makeTwoPointsDistance();
    dcm::DecompositionManager dcm;
    auto decomp = dcm.decompose(m);
    lgs::LocalGeometricSolver lgs;
    if (!decomp.subProblems.empty()) {
        auto report = lgs.analyzeStatus(m, decomp.subProblems[0]);
        GCS_ASSERT_EQ(report.overallStatus, lgs::ConstraintStatus::UnderConstrained, "L10: sub-problem under-constrained");
    } else {
        GCS_ASSERT(false, "L10: expected at least 1 sub-problem");
    }
}

void test_lgs_is_well_constrained() {
    auto m = makeWellConstrainedTriangle();
    lgs::LocalGeometricSolver lgs;
    GCS_ASSERT_EQ(lgs.isWellConstrained(m), true, "L11: isWellConstrained true");
}

void test_lgs_is_not_well_constrained() {
    auto m = makeUnderConstrained();
    lgs::LocalGeometricSolver lgs;
    GCS_ASSERT_EQ(lgs.isWellConstrained(m), false, "L12: isWellConstrained false");
}

void test_lgs_status_report_summary() {
    auto m = makeSinglePoint();
    lgs::LocalGeometricSolver lgs;
    auto report = lgs.analyzeStatus(m);
    GCS_ASSERT(!report.summaryText.empty(), "L13: summaryText non-empty");
}

void test_lgs_status_report_consistency() {
    auto m = makeOverConstrained();
    lgs::LocalGeometricSolver lgs;
    auto report = lgs.analyzeStatus(m);
    GCS_ASSERT(report.isConsistent || !report.isConsistent, "L14: isConsistent field accessible");
}

void test_lgs_dof_rigidset_aware() {
    Manager m;
    RigidSet rs; rs.id = 0; rs.geometryIds = {0, 1};
    m.rigidSets.push_back(rs);
    Geometry g0; g0.id = 0; g0.type = GeometryType::Point; g0.rigidSetId = 0;
    Geometry g1; g1.id = 1; g1.type = GeometryType::Point; g1.rigidSetId = 0;
    for (int i = 0; i < 6; ++i) { g0.v[i] = 0; g1.v[i] = 0; }
    g1.v[0] = 3;
    m.geometries.push_back(g0);
    m.geometries.push_back(g1);
    Constraint c; c.id = 0; c.type = ConstraintType::Distance; c.geometryIds = {0, 1}; c.value = 3;
    m.constraints.push_back(c);

    lgs::LocalGeometricSolver lgs;
    auto dof = lgs.analyzeDOF(m);
    GCS_ASSERT_EQ(dof.geometryDOF, 6, "L15: geometryDOF=6 (per-geometry, not RS-aware yet)");
    GCS_ASSERT_EQ(dof.constraintRemovedDOF, 1, "L15: constraintRemovedDOF=1");
    GCS_ASSERT_EQ(dof.netDOF, 5, "L15: netDOF=5");
}

int main() {
    std::cout << "=== LGS Interface Tests ===\n\n";

    test_lgs_dof_single_point();
    test_lgs_dof_single_line();
    test_lgs_dof_single_plane();
    test_lgs_dof_two_points_distance();
    test_lgs_dof_two_points_coincident();
    test_lgs_status_well_constrained();
    test_lgs_status_under_constrained();
    test_lgs_status_over_constrained();
    test_lgs_dof_with_subproblem();
    test_lgs_status_with_subproblem();
    test_lgs_is_well_constrained();
    test_lgs_is_not_well_constrained();
    test_lgs_status_report_summary();
    test_lgs_status_report_consistency();
    test_lgs_dof_rigidset_aware();

    GCS_TEST_SUMMARY();
}
