#include "test_framework.h"
#include "gcs/app/App.h"
#include <fstream>
#include <cstdio>

using namespace gcs;
using namespace gcs::app;

class ConcreteGeometry : public IGeometry {
    int id_;
    GeometryType type_;
    int rigidSetId_;
    std::array<double, 6> params_;
public:
    ConcreteGeometry(int id, GeometryType type, int rsId, std::array<double, 6> p)
        : id_(id), type_(type), rigidSetId_(rsId), params_(p) {}
    int id() const override { return id_; }
    GeometryType type() const override { return type_; }
    int rigidSetId() const override { return rigidSetId_; }
    std::array<double, 6> parameters() const override { return params_; }
};

class ConcreteConstraint : public IConstraint {
    int id_;
    ConstraintType type_;
    std::vector<int> geomIds_;
    double value_;
public:
    ConcreteConstraint(int id, ConstraintType type, std::vector<int> gids, double val)
        : id_(id), type_(type), geomIds_(std::move(gids)), value_(val) {}
    int id() const override { return id_; }
    ConstraintType type() const override { return type_; }
    const std::vector<int>& geometryIds() const override { return geomIds_; }
    double value() const override { return value_; }
};

class ConcreteRigidSet : public IRigidSet {
    int id_;
    std::vector<int> geomIds_;
public:
    ConcreteRigidSet(int id, std::vector<int> gids)
        : id_(id), geomIds_(std::move(gids)) {}
    int id() const override { return id_; }
    const std::vector<int>& geometryIds() const override { return geomIds_; }
};

class ConcreteProblem : public IProblem {
    std::vector<std::unique_ptr<IRigidSet>> rigidSets_;
    std::vector<std::unique_ptr<IGeometry>> geometries_;
    std::vector<std::unique_ptr<IConstraint>> constraints_;
public:
    ConcreteProblem(
        std::vector<std::unique_ptr<IRigidSet>> rs,
        std::vector<std::unique_ptr<IGeometry>> g,
        std::vector<std::unique_ptr<IConstraint>> c)
        : rigidSets_(std::move(rs))
        , geometries_(std::move(g))
        , constraints_(std::move(c)) {}

    const std::vector<std::unique_ptr<IRigidSet>>& rigidSets() const override { return rigidSets_; }
    const std::vector<std::unique_ptr<IGeometry>>& geometries() const override { return geometries_; }
    const std::vector<std::unique_ptr<IConstraint>>& constraints() const override { return constraints_; }
};

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
    App::instance().loadFile("test/app/full_pipeline.txt");
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

void test_app_iproblem_interface() {
    std::vector<std::unique_ptr<IRigidSet>> rs;
    rs.push_back(std::make_unique<ConcreteRigidSet>(0, std::vector<int>{0}));
    std::vector<std::unique_ptr<IGeometry>> g;
    g.push_back(std::make_unique<ConcreteGeometry>(0, GeometryType::Point, 0, std::array<double,6>{0,0,0,0,0,0}));
    std::vector<std::unique_ptr<IConstraint>> c;

    ConcreteProblem prob(std::move(rs), std::move(g), std::move(c));
    GCS_ASSERT_EQ(prob.rigidSets().size(), size_t(1), "A13: IProblem rigidSets");
    GCS_ASSERT_EQ(prob.geometries().size(), size_t(1), "A13: IProblem geometries");
    GCS_ASSERT_EQ(prob.constraints().size(), size_t(0), "A13: IProblem constraints");
}

void test_app_translate_problem() {
    std::vector<std::unique_ptr<IRigidSet>> rs;
    rs.push_back(std::make_unique<ConcreteRigidSet>(0, std::vector<int>{0, 1}));
    std::vector<std::unique_ptr<IGeometry>> g;
    g.push_back(std::make_unique<ConcreteGeometry>(0, GeometryType::Point, 0, std::array<double,6>{0,0,0,0,0,0}));
    g.push_back(std::make_unique<ConcreteGeometry>(1, GeometryType::Point, 0, std::array<double,6>{3,0,0,0,0,0}));
    std::vector<std::unique_ptr<IConstraint>> c;
    c.push_back(std::make_unique<ConcreteConstraint>(0, ConstraintType::Distance, std::vector<int>{0, 1}, 3.0));

    ConcreteProblem prob(std::move(rs), std::move(g), std::move(c));
    Manager m;
    translateProblem(prob, m);

    GCS_ASSERT_EQ(m.rigidSets.size(), size_t(1), "A14: translate RS count");
    GCS_ASSERT_EQ(m.geometries.size(), size_t(2), "A14: translate geom count");
    GCS_ASSERT_EQ(m.constraints.size(), size_t(1), "A14: translate constr count");
    GCS_ASSERT_EQ(m.geometries[1].v[0], 3.0, "A14: translate geom params");
    GCS_ASSERT_EQ(m.constraints[0].value, 3.0, "A14: translate constr value");
}

void test_app_load_problem() {
    std::vector<std::unique_ptr<IRigidSet>> rs;
    rs.push_back(std::make_unique<ConcreteRigidSet>(0, std::vector<int>{0}));
    std::vector<std::unique_ptr<IGeometry>> g;
    g.push_back(std::make_unique<ConcreteGeometry>(0, GeometryType::Point, 0, std::array<double,6>{1,2,3,0,0,0}));
    std::vector<std::unique_ptr<IConstraint>> c;

    ConcreteProblem prob(std::move(rs), std::move(g), std::move(c));
    App::instance().reset();
    App::instance().loadProblem(prob);

    GCS_ASSERT_EQ(App::instance().manager().geometries.size(), size_t(1), "A15: loadProblem geom count");
    GCS_ASSERT_NEAR(App::instance().manager().geometries[0].v[0], 1.0, 1e-10, "A15: loadProblem geom params");
    App::instance().reset();
}

void test_app_igeometry_interface() {
    ConcreteGeometry geom(42, GeometryType::Line, 3, std::array<double,6>{1,2,3,4,5,6});
    IGeometry& iface = geom;
    GCS_ASSERT_EQ(iface.id(), 42, "A16: IGeometry id");
    GCS_ASSERT_EQ(iface.type(), GeometryType::Line, "A16: IGeometry type");
    GCS_ASSERT_EQ(iface.rigidSetId(), 3, "A16: IGeometry rigidSetId");
    GCS_ASSERT_NEAR(iface.parameters()[0], 1.0, 1e-10, "A16: IGeometry params[0]");
}

void test_app_iconstraint_interface() {
    ConcreteConstraint constr(7, ConstraintType::Angle, {0, 1}, 1.57);
    IConstraint& iface = constr;
    GCS_ASSERT_EQ(iface.id(), 7, "A17: IConstraint id");
    GCS_ASSERT_EQ(iface.type(), ConstraintType::Angle, "A17: IConstraint type");
    GCS_ASSERT_EQ(iface.geometryIds().size(), size_t(2), "A17: IConstraint geomIds size");
    GCS_ASSERT_NEAR(iface.value(), 1.57, 1e-10, "A17: IConstraint value");
}

void test_app_irigidset_interface() {
    ConcreteRigidSet rs(5, {10, 20, 30});
    IRigidSet& iface = rs;
    GCS_ASSERT_EQ(iface.id(), 5, "A18: IRigidSet id");
    GCS_ASSERT_EQ(iface.geometryIds().size(), size_t(3), "A18: IRigidSet geomIds size");
    GCS_ASSERT_EQ(iface.geometryIds()[1], 20, "A18: IRigidSet geomIds[1]");
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
    test_app_iproblem_interface();
    test_app_translate_problem();
    test_app_load_problem();
    test_app_igeometry_interface();
    test_app_iconstraint_interface();
    test_app_irigidset_interface();

    GCS_TEST_SUMMARY();
}
