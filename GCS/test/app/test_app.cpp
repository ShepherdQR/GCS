#include "test_framework.h"
#include "app/App.h"

using namespace gcs;
using namespace gcs::app;

void test_app_add_rigidset() {
    App::instance().reset();
    App::instance().addRigidSet(0);
    GCS_ASSERT_EQ(App::instance().manager().rigidSets.size(), size_t(1), "A01: addRigidSet count");
    GCS_ASSERT_EQ(App::instance().manager().rigidSets[0].id, 0, "A01: addRigidSet id");
    App::instance().reset();
}

void test_app_add_geometry() {
    App::instance().reset();
    App::instance().addRigidSet(0).addGeometry(0, GeometryType::Point, 0);
    GCS_ASSERT_EQ(App::instance().manager().geometries.size(), size_t(1), "A02: addGeometry count");
    GCS_ASSERT_EQ(App::instance().manager().geometries[0].type, GeometryType::Point, "A02: addGeometry type");
    App::instance().reset();
}

void test_app_add_geometry_params() {
    App::instance().reset();
    App::instance().addRigidSet(0).addGeometry(0, GeometryType::Point, 0, {1, 2, 3, 0, 0, 0});
    GCS_ASSERT_NEAR(App::instance().manager().geometries[0].v[0], 1.0, 1e-10, "A03: v[0]=1");
    GCS_ASSERT_NEAR(App::instance().manager().geometries[0].v[1], 2.0, 1e-10, "A03: v[1]=2");
    GCS_ASSERT_NEAR(App::instance().manager().geometries[0].v[2], 3.0, 1e-10, "A03: v[2]=3");
    App::instance().reset();
}

void test_app_add_constraint() {
    App::instance().reset();
    App::instance().addRigidSet(0)
        .addGeometry(0, GeometryType::Point, 0)
        .addGeometry(1, GeometryType::Point, 0)
        .addConstraint(0, ConstraintType::Distance, {0, 1}, 5.0);
    GCS_ASSERT_EQ(App::instance().manager().constraints.size(), size_t(1), "A04: addConstraint count");
    GCS_ASSERT_EQ(App::instance().manager().constraints[0].type, ConstraintType::Distance, "A04: constraint type");
    GCS_ASSERT_NEAR(App::instance().manager().constraints[0].value, 5.0, 1e-10, "A04: constraint value");
    App::instance().reset();
}

void test_app_builder_chain() {
    App::instance().reset();
    App::instance()
        .addRigidSet(0)
        .addGeometry(0, GeometryType::Point, 0)
        .addGeometry(1, GeometryType::Point, 0)
        .addConstraint(0, ConstraintType::Distance, {0, 1}, 5.0);

    GCS_ASSERT_EQ(App::instance().manager().rigidSets.size(), size_t(1), "A05: builder RS count");
    GCS_ASSERT_EQ(App::instance().manager().geometries.size(), size_t(2), "A05: builder geom count");
    GCS_ASSERT_EQ(App::instance().manager().constraints.size(), size_t(1), "A05: builder constr count");
    App::instance().reset();
}

void test_app_load_file() {
    App::instance().reset();
    App::instance().loadFile("scene/test/app/full_pipeline.txt");
    GCS_ASSERT(App::instance().manager().geometries.size() > 0, "A06: loadFile geometries populated");
    App::instance().reset();
}

void test_app_compute() {
    App::instance().reset();
    App::instance()
        .addRigidSet(0)
        .addGeometry(0, GeometryType::Point, 0)
        .addGeometry(1, GeometryType::Point, 0)
        .addConstraint(0, ConstraintType::Distance, {0, 1}, 5.0)
        .compute();

    auto& status = App::instance().globalStatus();
    bool validStatus = (status.overallStatus == lgs::ConstraintStatus::WellConstrained ||
                        status.overallStatus == lgs::ConstraintStatus::UnderConstrained ||
                        status.overallStatus == lgs::ConstraintStatus::OverConstrained ||
                        status.overallStatus == lgs::ConstraintStatus::OverConstrainedConsistent);
    GCS_ASSERT(validStatus, "A07: compute globalStatus populated");
    App::instance().reset();
}

void test_app_compute_decomposition() {
    App::instance().reset();
    App::instance()
        .addRigidSet(0)
        .addGeometry(0, GeometryType::Point, 0)
        .addGeometry(1, GeometryType::Point, 0)
        .addConstraint(0, ConstraintType::Distance, {0, 1}, 5.0)
        .compute();

    auto& decomp = App::instance().decomposition();
    GCS_ASSERT(decomp.subProblems.size() >= 1, "A08: decomposition populated");
    App::instance().reset();
}

void test_app_get_transformation() {
    App::instance().reset();
    App::instance()
        .addRigidSet(0)
        .addGeometry(0, GeometryType::Point, 0, {1, 2, 3, 0, 0, 0})
        .compute();

    auto& t = App::instance().getTransformation(0);
    GCS_ASSERT_NEAR(t[0], 1.0, 1e-10, "A09: getTransformation v[0]");
    GCS_ASSERT_NEAR(t[1], 2.0, 1e-10, "A09: getTransformation v[1]");
    GCS_ASSERT_NEAR(t[2], 3.0, 1e-10, "A09: getTransformation v[2]");
    App::instance().reset();
}

void test_app_get_transformation_missing() {
    App::instance().reset();
    App::instance()
        .addRigidSet(0)
        .addGeometry(0, GeometryType::Point, 0)
        .compute();

    auto& t = App::instance().getTransformation(99);
    GCS_ASSERT_NEAR(t[0], 0.0, 1e-10, "A10: missing RS returns zero");
    App::instance().reset();
}

void test_app_reset() {
    App::instance().reset();
    App::instance()
        .addRigidSet(0)
        .addGeometry(0, GeometryType::Point, 0)
        .addConstraint(0, ConstraintType::Distance, {0}, 1.0);

    App::instance().reset();
    GCS_ASSERT_EQ(App::instance().manager().rigidSets.size(), size_t(0), "A11: reset RS empty");
    GCS_ASSERT_EQ(App::instance().manager().geometries.size(), size_t(0), "A11: reset geom empty");
    GCS_ASSERT_EQ(App::instance().manager().constraints.size(), size_t(0), "A11: reset constr empty");
}

void test_app_reset_reuse() {
    App::instance().reset();
    App::instance().addRigidSet(0).addGeometry(0, GeometryType::Point, 0);
    App::instance().reset();
    App::instance().addRigidSet(5).addGeometry(10, GeometryType::Line, 5);

    GCS_ASSERT_EQ(App::instance().manager().rigidSets[0].id, 5, "A12: reuse RS id");
    GCS_ASSERT_EQ(App::instance().manager().geometries[0].id, 10, "A12: reuse geom id");
    GCS_ASSERT_EQ(App::instance().manager().geometries[0].type, GeometryType::Line, "A12: reuse geom type");
    App::instance().reset();
}

int main() {
    std::cout << "=== App Interface Tests ===\n\n";

    test_app_add_rigidset();
    test_app_add_geometry();
    test_app_add_geometry_params();
    test_app_add_constraint();
    test_app_builder_chain();
    test_app_load_file();
    test_app_compute();
    test_app_compute_decomposition();
    test_app_get_transformation();
    test_app_get_transformation_missing();
    test_app_reset();
    test_app_reset_reuse();

    GCS_TEST_SUMMARY();
}
