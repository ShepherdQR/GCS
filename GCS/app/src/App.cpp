#include "gcs/app/App.h"
#include <algorithm>

namespace gcs {
namespace app {

std::array<double, 6> App::zero_params_ = {0, 0, 0, 0, 0, 0};

App& App::instance() {
    static App inst;
    return inst;
}

App& App::addRigidSet(int id) {
    RigidSet rs;
    rs.id = id;
    manager_.rigidSets.push_back(rs);
    computed_ = false;
    return *this;
}

App& App::addGeometry(int id, GeometryType type, int rigidSetId,
                       const std::array<double, 6>& params) {
    Geometry g;
    g.id = id;
    g.type = type;
    g.rigidSetId = rigidSetId;
    for (int i = 0; i < 6; ++i) g.v[i] = params[i];
    manager_.geometries.push_back(g);

    auto* rs = manager_.findRigidSet(rigidSetId);
    if (rs) rs->geometryIds.push_back(id);

    computed_ = false;
    return *this;
}

App& App::addConstraint(int id, ConstraintType type,
                         const std::vector<int>& geomIds, double value) {
    Constraint c;
    c.id = id;
    c.type = type;
    c.geometryIds = geomIds;
    c.value = value;
    manager_.constraints.push_back(c);
    computed_ = false;
    return *this;
}

App& App::loadProblem(const IProblem& problem) {
    translateProblem(problem, manager_);
    computed_ = false;
    return *this;
}

App& App::loadFile(const std::string& path) {
    if (path.size() >= 5 && path.substr(path.size() - 5) == ".json") {
        io::readGraphJSON(manager_, path);
    } else {
        io::readGraph(manager_, path);
    }
    computed_ = false;
    return *this;
}

App& App::compute() {
    if (computed_) return *this;

    dcm::DecompositionManager dcmMgr;
    decomp_ = dcmMgr.decompose(manager_);

    lgs::LocalGeometricSolver lgs;
    globalStatus_ = lgs.analyzeStatus(manager_);

    solverReports_.clear();
    cds::ConstraintDrivenSolver solver;
    for (const auto& sp : decomp_.subProblems) {
        auto report = solver.solveSubProblem(manager_, sp);
        solverReports_.push_back(report);
    }

    transformations_.clear();
    for (const auto& rs : manager_.rigidSets) {
        std::array<double, 6> t = {0, 0, 0, 0, 0, 0};
        bool first = true;
        for (int gid : rs.geometryIds) {
            auto* g = manager_.findGeometry(gid);
            if (g) {
                if (first) {
                    for (int i = 0; i < 6; ++i) t[i] = g->v[i];
                    first = false;
                }
            }
        }
        transformations_[rs.id] = t;
    }

    computed_ = true;
    return *this;
}

const std::array<double, 6>& App::getTransformation(int rigidSetId) const {
    auto it = transformations_.find(rigidSetId);
    if (it != transformations_.end()) return it->second;
    return zero_params_;
}

const Manager& App::manager() const {
    return manager_;
}

const dcm::DecompositionResult& App::decomposition() const {
    return decomp_;
}

const lgs::StatusReport& App::globalStatus() const {
    return globalStatus_;
}

const std::vector<cds::SolverReport>& App::solverReports() const {
    return solverReports_;
}

App& App::reset() {
    manager_ = Manager();
    decomp_ = dcm::DecompositionResult();
    globalStatus_ = lgs::StatusReport();
    solverReports_.clear();
    transformations_.clear();
    computed_ = false;
    return *this;
}

void translateProblem(const IProblem& problem, Manager& m) {
    m = Manager();

    for (const auto& irs : problem.rigidSets()) {
        RigidSet rs;
        rs.id = irs->id();
        rs.geometryIds = irs->geometryIds();
        m.rigidSets.push_back(rs);
    }

    for (const auto& ig : problem.geometries()) {
        Geometry g;
        g.id = ig->id();
        g.type = ig->type();
        g.rigidSetId = ig->rigidSetId();
        auto params = ig->parameters();
        for (int i = 0; i < 6; ++i) g.v[i] = params[i];
        m.geometries.push_back(g);
    }

    for (const auto& ic : problem.constraints()) {
        Constraint c;
        c.id = ic->id();
        c.type = ic->type();
        c.geometryIds = ic->geometryIds();
        c.value = ic->value();
        m.constraints.push_back(c);
    }
}

} // namespace app
} // namespace gcs
