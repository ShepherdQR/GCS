#include "test_framework.h"
#include "gcs/dcm/dcm.h"
#include "gcs/io/io.h"

using namespace gcs;

static Manager makeTwoDisconnected() {
    Manager m;
    RigidSet rs0; rs0.id = 0;
    RigidSet rs1; rs1.id = 1;
    m.rigidSets.push_back(rs0);
    m.rigidSets.push_back(rs1);

    Geometry g0; g0.id = 0; g0.type = GeometryType::Point; g0.rigidSetId = 0;
    Geometry g1; g1.id = 1; g1.type = GeometryType::Point; g0.rigidSetId = 0;
    g1.rigidSetId = 0;
    Geometry g2; g2.id = 2; g2.type = GeometryType::Point; g2.rigidSetId = 1;
    Geometry g3; g3.id = 3; g3.type = GeometryType::Point; g3.rigidSetId = 1;
    for (int i = 0; i < 6; ++i) { g0.v[i] = 0; g1.v[i] = 0; g2.v[i] = 0; g3.v[i] = 0; }
    m.geometries.push_back(g0);
    m.geometries.push_back(g1);
    m.geometries.push_back(g2);
    m.geometries.push_back(g3);

    Constraint c0; c0.id = 0; c0.type = ConstraintType::Distance; c0.geometryIds = {0, 1}; c0.value = 3;
    Constraint c1; c1.id = 1; c1.type = ConstraintType::Distance; c1.geometryIds = {2, 3}; c1.value = 4;
    m.constraints.push_back(c0);
    m.constraints.push_back(c1);

    rs0.geometryIds = {0, 1};
    rs1.geometryIds = {2, 3};
    m.rigidSets[0].geometryIds = {0, 1};
    m.rigidSets[1].geometryIds = {2, 3};

    return m;
}

void test_dcm_decompose_empty() {
    Manager m;
    dcm::DecompositionManager dcm;
    auto result = dcm.decompose(m);
    GCS_ASSERT_EQ(result.subProblems.size(), size_t(0), "D01: empty Manager 0 sub-problems");
}

void test_dcm_decompose_single_geometry() {
    Manager m;
    RigidSet rs; rs.id = 0; rs.geometryIds = {0};
    m.rigidSets.push_back(rs);
    Geometry g; g.id = 0; g.type = GeometryType::Point; g.rigidSetId = 0;
    for (int i = 0; i < 6; ++i) g.v[i] = 0;
    m.geometries.push_back(g);

    dcm::DecompositionManager dcm;
    auto result = dcm.decompose(m);
    GCS_ASSERT_EQ(result.subProblems.size(), size_t(1), "D02: single geometry 1 sub-problem");
    if (!result.subProblems.empty()) {
        GCS_ASSERT_EQ(result.subProblems[0].geometryIds.size(), size_t(1), "D02: sub-problem has 1 geometry");
    }
}

void test_dcm_decompose_two_disconnected() {
    Manager m;
    RigidSet rs0; rs0.id = 0; rs0.geometryIds = {0};
    RigidSet rs1; rs1.id = 1; rs1.geometryIds = {1};
    m.rigidSets.push_back(rs0);
    m.rigidSets.push_back(rs1);
    Geometry g0; g0.id = 0; g0.type = GeometryType::Point; g0.rigidSetId = 0;
    Geometry g1; g1.id = 1; g1.type = GeometryType::Point; g1.rigidSetId = 1;
    for (int i = 0; i < 6; ++i) { g0.v[i] = 0; g1.v[i] = 0; }
    m.geometries.push_back(g0);
    m.geometries.push_back(g1);

    dcm::DecompositionManager dcm;
    auto result = dcm.decompose(m);
    GCS_ASSERT_EQ(result.subProblems.size(), size_t(2), "D03: two disconnected 2 sub-problems");
}

void test_dcm_decompose_two_connected() {
    Manager m;
    RigidSet rs0; rs0.id = 0; rs0.geometryIds = {0, 1};
    m.rigidSets.push_back(rs0);
    Geometry g0; g0.id = 0; g0.type = GeometryType::Point; g0.rigidSetId = 0;
    Geometry g1; g1.id = 1; g1.type = GeometryType::Point; g1.rigidSetId = 0;
    for (int i = 0; i < 6; ++i) { g0.v[i] = 0; g1.v[i] = 0; }
    m.geometries.push_back(g0);
    m.geometries.push_back(g1);

    Constraint c; c.id = 0; c.type = ConstraintType::Distance; c.geometryIds = {0, 1}; c.value = 5;
    m.constraints.push_back(c);

    dcm::DecompositionManager dcm;
    auto result = dcm.decompose(m);
    GCS_ASSERT_EQ(result.subProblems.size(), size_t(1), "D04: two connected 1 sub-problem");
    if (!result.subProblems.empty()) {
        GCS_ASSERT_EQ(result.subProblems[0].geometryIds.size(), size_t(2), "D04: sub-problem has 2 geometries");
    }
}

void test_dcm_decompose_chain() {
    Manager m;
    RigidSet rs; rs.id = 0; rs.geometryIds = {0, 1, 2, 3, 4};
    m.rigidSets.push_back(rs);
    for (int i = 0; i < 5; ++i) {
        Geometry g; g.id = i; g.type = GeometryType::Point; g.rigidSetId = 0;
        for (int k = 0; k < 6; ++k) g.v[k] = 0;
        m.geometries.push_back(g);
    }
    for (int i = 0; i < 4; ++i) {
        Constraint c; c.id = i; c.type = ConstraintType::Distance; c.geometryIds = {i, i + 1}; c.value = 1;
        m.constraints.push_back(c);
    }

    dcm::DecompositionManager dcm;
    auto result = dcm.decompose(m);
    GCS_ASSERT_EQ(result.subProblems.size(), size_t(1), "D05: chain 1 sub-problem");
    if (!result.subProblems.empty()) {
        GCS_ASSERT_EQ(result.subProblems[0].geometryIds.size(), size_t(5), "D05: sub-problem has 5 geometries");
    }
}

void test_dcm_decompose_two_components() {
    auto m = makeTwoDisconnected();
    dcm::DecompositionManager dcm;
    auto result = dcm.decompose(m);
    GCS_ASSERT_EQ(result.subProblems.size(), size_t(2), "D06: two components 2 sub-problems");
}

void test_dcm_decompose_rigidset_grouping() {
    Manager m;
    RigidSet rs; rs.id = 0; rs.geometryIds = {0, 1};
    m.rigidSets.push_back(rs);
    Geometry g0; g0.id = 0; g0.type = GeometryType::Point; g0.rigidSetId = 0;
    Geometry g1; g1.id = 1; g1.type = GeometryType::Point; g1.rigidSetId = 0;
    for (int i = 0; i < 6; ++i) { g0.v[i] = 0; g1.v[i] = 0; }
    m.geometries.push_back(g0);
    m.geometries.push_back(g1);

    dcm::DecompositionManager dcm;
    auto result = dcm.decompose(m);
    GCS_ASSERT_EQ(result.subProblems.size(), size_t(1), "D07: same RS same sub-problem");
    if (!result.subProblems.empty()) {
        GCS_ASSERT_EQ(result.subProblems[0].geometryIds.size(), size_t(2), "D07: both geometries in same sub-problem");
    }
}

void test_dcm_decompose_result_counts() {
    auto m = makeTwoDisconnected();
    dcm::DecompositionManager dcm;
    auto result = dcm.decompose(m);
    GCS_ASSERT_EQ(result.totalGeometries, 4, "D08: totalGeometries");
    GCS_ASSERT_EQ(result.totalConstraints, 2, "D08: totalConstraints");
}

void test_dcm_decompose_is_single_component() {
    Manager m1;
    RigidSet rs; rs.id = 0; rs.geometryIds = {0, 1};
    m1.rigidSets.push_back(rs);
    Geometry g0; g0.id = 0; g0.type = GeometryType::Point; g0.rigidSetId = 0;
    Geometry g1; g1.id = 1; g1.type = GeometryType::Point; g1.rigidSetId = 0;
    for (int i = 0; i < 6; ++i) { g0.v[i] = 0; g1.v[i] = 0; }
    m1.geometries.push_back(g0);
    m1.geometries.push_back(g1);
    Constraint c; c.id = 0; c.type = ConstraintType::Distance; c.geometryIds = {0, 1}; c.value = 5;
    m1.constraints.push_back(c);

    dcm::DecompositionManager dcm;
    auto r1 = dcm.decompose(m1);
    GCS_ASSERT_EQ(r1.isSingleComponent, true, "D09: single component true");

    auto m2 = makeTwoDisconnected();
    auto r2 = dcm.decompose(m2);
    GCS_ASSERT_EQ(r2.isSingleComponent, false, "D09: two components false");
}

void test_dcm_decompose_subproblem_ids() {
    auto m = makeTwoDisconnected();
    dcm::DecompositionManager dcm;
    auto result = dcm.decompose(m);
    if (result.subProblems.size() >= 2) {
        GCS_ASSERT_EQ(result.subProblems[0].id, 0, "D10: sub-problem 0 id");
        GCS_ASSERT_EQ(result.subProblems[1].id, 1, "D10: sub-problem 1 id");
    } else {
        GCS_ASSERT(false, "D10: expected 2 sub-problems");
    }
}

void test_dcm_decompose_subproblem_constraints() {
    auto m = makeTwoDisconnected();
    dcm::DecompositionManager dcm;
    auto result = dcm.decompose(m);
    if (result.subProblems.size() >= 2) {
        GCS_ASSERT_EQ(result.subProblems[0].constraintIds.size(), size_t(1), "D11: sub-problem 0 has 1 constraint");
        GCS_ASSERT_EQ(result.subProblems[1].constraintIds.size(), size_t(1), "D11: sub-problem 1 has 1 constraint");
    } else {
        GCS_ASSERT(false, "D11: expected 2 sub-problems");
    }
}

void test_dcm_extract_subproblem() {
    auto m = makeTwoDisconnected();
    dcm::DecompositionManager dcm;
    auto sp = dcm.extractSubProblem(m, {0, 1});
    GCS_ASSERT_EQ(sp.geometryIds.size(), size_t(2), "D12: extractSubProblem geometryIds size");
    GCS_ASSERT(sp.constraintIds.size() >= size_t(1), "D12: extractSubProblem has constraints");
}

int main() {
    std::cout << "=== DCM Interface Tests ===\n\n";

    test_dcm_decompose_empty();
    test_dcm_decompose_single_geometry();
    test_dcm_decompose_two_disconnected();
    test_dcm_decompose_two_connected();
    test_dcm_decompose_chain();
    test_dcm_decompose_two_components();
    test_dcm_decompose_rigidset_grouping();
    test_dcm_decompose_result_counts();
    test_dcm_decompose_is_single_component();
    test_dcm_decompose_subproblem_ids();
    test_dcm_decompose_subproblem_constraints();
    test_dcm_extract_subproblem();

    GCS_TEST_SUMMARY();
}
