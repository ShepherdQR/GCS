#include "lgs/lgs.h"
#include <cmath>
#include <sstream>

namespace gcs {
namespace lgs {

std::string toString(ConstraintStatus status) {
    switch (status) {
        case ConstraintStatus::WellConstrained:            return "WellConstrained";
        case ConstraintStatus::UnderConstrained:           return "UnderConstrained";
        case ConstraintStatus::OverConstrained:            return "OverConstrained";
        case ConstraintStatus::OverConstrainedConsistent:  return "OverConstrainedConsistent";
    }
    return "Unknown";
}

ConstraintStatus LocalGeometricSolver::classifyStatus(int netDOF) const {
    if (netDOF == 0) return ConstraintStatus::WellConstrained;
    if (netDOF > 0)  return ConstraintStatus::UnderConstrained;
    return ConstraintStatus::OverConstrained;
}

ConstraintStatus LocalGeometricSolver::classifyStatusWithRigidSets(
    const Manager& m, const dcm::SubProblem& sp, int netDOF) const {
    int nRS = (int)sp.rigidSetIds.size();
    if (nRS <= 1) {
        if (netDOF == 6) return ConstraintStatus::WellConstrained;
        if (netDOF > 6)  return ConstraintStatus::UnderConstrained;
        return ConstraintStatus::OverConstrained;
    } else {
        if (netDOF == 0) return ConstraintStatus::WellConstrained;
        if (netDOF > 0)  return ConstraintStatus::UnderConstrained;
        return ConstraintStatus::OverConstrained;
    }
}

int LocalGeometricSolver::computeGeometryDOF(
    const Manager& m, const dcm::SubProblem& sp) const {
    int dof = 0;
    for (int gid : sp.geometryIds) {
        const auto* g = m.findGeometry(gid);
        if (g) dof += dofGeometry(g->type);
    }
    return dof;
}

int LocalGeometricSolver::computeConstraintRemovedDOF(
    const Manager& m, const dcm::SubProblem& sp) const {
    int removed = 0;
    for (int cid : sp.constraintIds) {
        const auto* c = m.findConstraint(cid);
        if (c) removed += dofRemovedConstraint(c->type);
    }
    return removed;
}

DOFAnalysis LocalGeometricSolver::analyzeDOF(const Manager& m) const {
    dcm::SubProblem all;
    all.id = 0;
    for (const auto& g : m.geometries) all.geometryIds.push_back(g.id);
    for (const auto& c : m.constraints) all.constraintIds.push_back(c.id);
    for (const auto& rs : m.rigidSets) all.rigidSetIds.push_back(rs.id);
    return analyzeDOF(m, all);
}

DOFAnalysis LocalGeometricSolver::analyzeDOF(
    const Manager& m, const dcm::SubProblem& sp) const {
    DOFAnalysis analysis;
    analysis.geometryDOF = computeGeometryDOF(m, sp);
    analysis.constraintRemovedDOF = computeConstraintRemovedDOF(m, sp);
    analysis.netDOF = analysis.geometryDOF - analysis.constraintRemovedDOF;
    analysis.status = classifyStatus(analysis.netDOF);
    return analysis;
}

StatusReport LocalGeometricSolver::analyzeStatus(const Manager& m) const {
    dcm::SubProblem all;
    all.id = 0;
    for (const auto& g : m.geometries) all.geometryIds.push_back(g.id);
    for (const auto& c : m.constraints) all.constraintIds.push_back(c.id);
    for (const auto& rs : m.rigidSets) all.rigidSetIds.push_back(rs.id);
    return analyzeStatus(m, all);
}

StatusReport LocalGeometricSolver::analyzeStatus(
    const Manager& m, const dcm::SubProblem& sp) const {
    StatusReport report;
    report.dofAnalysis = analyzeDOF(m, sp);
    report.overallStatus = classifyStatusWithRigidSets(m, sp, report.dofAnalysis.netDOF);
    report.isConsistent = true;

    std::ostringstream oss;
    oss << "DOF: " << report.dofAnalysis.geometryDOF
        << " - " << report.dofAnalysis.constraintRemovedDOF
        << " = " << report.dofAnalysis.netDOF
        << " (" << toString(report.overallStatus) << ")";
    report.summaryText = oss.str();

    return report;
}

double LocalGeometricSolver::computeConstraintResidual(
    const Manager& m, const Constraint& c) const {
    if (c.geometryIds.size() < 2) return 0.0;

    const auto* g1 = m.findGeometry(c.geometryIds[0]);
    const auto* g2 = m.findGeometry(c.geometryIds[1]);
    if (!g1 || !g2) return 0.0;

    switch (c.type) {
        case ConstraintType::Coincident: {
            double dx = g2->v[0] - g1->v[0];
            double dy = g2->v[1] - g1->v[1];
            double dz = g2->v[2] - g1->v[2];
            return std::sqrt(dx*dx + dy*dy + dz*dz);
        }
        case ConstraintType::Distance: {
            double dx = g2->v[0] - g1->v[0];
            double dy = g2->v[1] - g1->v[1];
            double dz = g2->v[2] - g1->v[2];
            return std::abs(std::sqrt(dx*dx + dy*dy + dz*dz) - c.value);
        }
        default:
            return 0.0;
    }
}

std::vector<ConstraintViolation> LocalGeometricSolver::checkSatisfaction(
    const Manager& m, double tolerance) const {
    std::vector<ConstraintViolation> violations;
    for (const auto& c : m.constraints) {
        double residual = computeConstraintResidual(m, c);
        violations.push_back({c.id, residual, tolerance, residual < tolerance});
    }
    return violations;
}

bool LocalGeometricSolver::isWellConstrained(const Manager& m) const {
    return analyzeDOF(m).status == ConstraintStatus::WellConstrained;
}

}
}
