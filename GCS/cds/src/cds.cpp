#include "gcs/cds/cds.h"
#include <cmath>
#include <algorithm>
#include <array>
#include <iostream>

namespace gcs {
namespace cds {

std::string toString(SolverResult result) {
    switch (result) {
        case SolverResult::Converged:              return "Converged";
        case SolverResult::Diverged:               return "Diverged";
        case SolverResult::MaxIterationsReached:   return "MaxIterationsReached";
        case SolverResult::SingularJacobian:       return "SingularJacobian";
        case SolverResult::InconsistentConstraints: return "InconsistentConstraints";
    }
    return "Unknown";
}

ConstraintDrivenSolver::ConstraintDrivenSolver(const SolverConfig& config)
    : config_(config) {}

void ConstraintDrivenSolver::setConfig(const SolverConfig& config) {
    config_ = config;
}

const SolverConfig& ConstraintDrivenSolver::config() const {
    return config_;
}

SolverReport ConstraintDrivenSolver::solve(Manager& m) {
    dcm::DecompositionManager dcmMgr;
    auto decomp = dcmMgr.decompose(m);

    SolverReport finalReport;
    finalReport.result = SolverResult::Converged;
    finalReport.iterationsUsed = 0;
    finalReport.initialResidual = 0.0;
    finalReport.finalResidual = 0.0;

    for (const auto& sp : decomp.subProblems) {
        auto report = solveSubProblem(m, sp);
        finalReport.iterationsUsed += report.iterationsUsed;
        finalReport.initialResidual += report.initialResidual;
        finalReport.finalResidual += report.finalResidual;
        if (report.result != SolverResult::Converged) {
            finalReport.result = report.result;
        }
    }

    return finalReport;
}

static double computeConstraintResidual(
    const Manager& m, const Constraint& c) {
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
            return std::sqrt(dx*dx + dy*dy + dz*dz) - c.value;
        }
        default:
            return 0.0;
    }
}

static bool solveLinearSystem(
    const std::vector<double>& A,
    const std::vector<double>& b,
    std::vector<double>& x,
    int n, int m) {

    std::vector<double> aug(n * (m + 1));
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            aug[i * (m + 1) + j] = A[i * m + j];
        }
        aug[i * (m + 1) + m] = b[i];
    }

    int rank = 0;
    for (int col = 0; col < m && rank < n; col++) {
        int pivot = -1;
        double maxVal = 1e-12;
        for (int row = rank; row < n; row++) {
            double val = std::abs(aug[row * (m + 1) + col]);
            if (val > maxVal) {
                maxVal = val;
                pivot = row;
            }
        }
        if (pivot < 0) continue;

        if (pivot != rank) {
            for (int j = 0; j <= m; j++) {
                std::swap(aug[rank * (m + 1) + j], aug[pivot * (m + 1) + j]);
            }
        }

        double diag = aug[rank * (m + 1) + col];
        if (std::abs(diag) < 1e-15) continue;

        for (int j = 0; j <= m; j++) {
            aug[rank * (m + 1) + j] /= diag;
        }

        for (int row = 0; row < n; row++) {
            if (row == rank) continue;
            double factor = aug[row * (m + 1) + col];
            for (int j = 0; j <= m; j++) {
                aug[row * (m + 1) + j] -= factor * aug[rank * (m + 1) + j];
            }
        }
        rank++;
    }

    x.assign(m, 0.0);
    int col = 0;
    for (int i = 0; i < rank && col < m; i++) {
        while (col < m && std::abs(aug[i * (m + 1) + col]) < 1e-10) col++;
        if (col < m) {
            x[col] = aug[i * (m + 1) + m];
            col++;
        }
    }

    return true;
}

SolverReport ConstraintDrivenSolver::solveSubProblem(
    Manager& m, const dcm::SubProblem& sp) {
    SolverReport report;
    report.result = SolverResult::MaxIterationsReached;
    report.iterationsUsed = 0;
    report.initialResidual = 0.0;
    report.finalResidual = 0.0;

    int nConstraints = (int)sp.constraintIds.size();

    int nPointCoords = 0;
    for (int gid : sp.geometryIds) {
        const auto* g = m.findGeometry(gid);
        if (g && g->type == GeometryType::Point) nPointCoords += 3;
    }

    if (nPointCoords == 0 || nConstraints == 0) {
        report.result = SolverResult::Converged;
        return report;
    }

    int nFreeVars = nPointCoords;
    if (sp.rigidSetIds.size() <= 1 && nPointCoords >= 6) {
        nFreeVars = nPointCoords - 6;
    } else if (nPointCoords >= 3) {
        nFreeVars = nPointCoords - 3;
    }
    if (nFreeVars < 0) nFreeVars = 0;

    auto computeTotalResidual = [&]() -> double {
        double total = 0.0;
        for (int cid : sp.constraintIds) {
            const auto* c = m.findConstraint(cid);
            double r = computeConstraintResidual(m, *c);
            total += r * r;
        }
        return std::sqrt(total);
    };

    report.initialResidual = computeTotalResidual();

    if (report.initialResidual < config_.tolerance) {
        report.result = SolverResult::Converged;
        report.finalResidual = report.initialResidual;
        return report;
    }

    if (nFreeVars == 0) {
        report.result = SolverResult::Converged;
        report.finalResidual = report.initialResidual;
        return report;
    }

    std::cerr << "[CDS] nFreeVars=" << nFreeVars
              << " nConstraints=" << nConstraints
              << " initialResidual=" << report.initialResidual << "\n";

    int fixedVars = nPointCoords - nFreeVars;
    double lmDamping = 1e-6;

    auto saveCoords = [&](std::vector<std::array<double, 6>>& saved) {
        saved.clear();
        for (int gid : sp.geometryIds) {
            const auto* g = m.findGeometry(gid);
            if (g) {
                std::array<double, 6> arr;
                for (int k = 0; k < 6; k++) arr[k] = g->v[k];
                saved.push_back(arr);
            }
        }
    };

    auto restoreCoords = [&](const std::vector<std::array<double, 6>>& saved) {
        for (size_t gi = 0; gi < sp.geometryIds.size(); gi++) {
            auto* g = m.findGeometry(sp.geometryIds[gi]);
            if (g) {
                for (int k = 0; k < 6; k++) g->v[k] = saved[gi][k];
            }
        }
    };

    auto applyDelta = [&](const std::vector<std::array<double, 6>>& saved,
                          const std::vector<double>& delta, double alpha) {
        for (size_t gi = 0; gi < sp.geometryIds.size(); gi++) {
            auto* g = m.findGeometry(sp.geometryIds[gi]);
            if (!g || g->type != GeometryType::Point) continue;
            for (int c = 0; c < 3; c++) {
                int globalVi = (int)gi * 3 + c;
                if (globalVi >= fixedVars) {
                    int localVi = globalVi - fixedVars;
                    if (localVi < nFreeVars) {
                        g->v[c] = saved[gi][c] + alpha * delta[localVi];
                    }
                }
            }
        }
    };

    for (int iter = 0; iter < config_.maxIterations; iter++) {
        report.iterationsUsed = iter + 1;

        double currentResidual = computeTotalResidual();
        if (currentResidual < config_.tolerance) {
            report.result = SolverResult::Converged;
            report.finalResidual = currentResidual;
            return report;
        }

        std::vector<double> J(nConstraints * nFreeVars, 0.0);

        const double eps = 1e-8;
        std::vector<double> residuals(nConstraints);
        for (int i = 0; i < nConstraints; i++) {
            const auto* c = m.findConstraint(sp.constraintIds[i]);
            residuals[i] = computeConstraintResidual(m, *c);
        }

        for (int vi = 0; vi < nFreeVars; vi++) {
            int globalVi = vi + fixedVars;
            int geomIdx = globalVi / 3;
            int coordIdx = globalVi % 3;

            if (geomIdx >= (int)sp.geometryIds.size()) continue;
            int gid = sp.geometryIds[geomIdx];
            auto* g = m.findGeometry(gid);
            if (!g) continue;

            double orig = g->v[coordIdx];
            g->v[coordIdx] = orig + eps;

            for (int ci = 0; ci < nConstraints; ci++) {
                const auto* c = m.findConstraint(sp.constraintIds[ci]);
                double r1 = computeConstraintResidual(m, *c);
                J[ci * nFreeVars + vi] = (r1 - residuals[ci]) / eps;
            }

            g->v[coordIdx] = orig;
        }

        std::vector<double> delta(nFreeVars, 0.0);

        if (nConstraints >= nFreeVars) {
            std::vector<double> negR(nConstraints);
            for (int i = 0; i < nConstraints; i++) {
                negR[i] = -residuals[i];
            }
            solveLinearSystem(J, negR, delta, nConstraints, nFreeVars);
        } else {
            std::vector<double> JtJ(nFreeVars * nFreeVars, 0.0);
            std::vector<double> Jtr(nFreeVars, 0.0);

            for (int i = 0; i < nFreeVars; i++) {
                for (int j = 0; j < nFreeVars; j++) {
                    double sum = 0.0;
                    for (int k = 0; k < nConstraints; k++) {
                        sum += J[k * nFreeVars + i] * J[k * nFreeVars + j];
                    }
                    JtJ[i * nFreeVars + j] = sum;
                }
                JtJ[i * nFreeVars + i] += lmDamping * (1.0 + std::abs(JtJ[i * nFreeVars + i]));

                double sum = 0.0;
                for (int k = 0; k < nConstraints; k++) {
                    sum += J[k * nFreeVars + i] * (-residuals[k]);
                }
                Jtr[i] = sum;
            }

            solveLinearSystem(JtJ, Jtr, delta, nFreeVars, nFreeVars);
        }

        std::vector<std::array<double, 6>> savedCoords;
        saveCoords(savedCoords);

        double alpha = 1.0;
        double bestAlpha = 0.0;
        double bestResidual = currentResidual;

        for (int ls = 0; ls < 20; ls++) {
            applyDelta(savedCoords, delta, alpha);
            double newResidual = computeTotalResidual();
            if (newResidual < bestResidual) {
                bestResidual = newResidual;
                bestAlpha = alpha;
            }
            restoreCoords(savedCoords);
            alpha *= 0.5;
            if (alpha < 1e-14) break;
        }

        if (bestAlpha > 0.0) {
            applyDelta(savedCoords, delta, bestAlpha);
            lmDamping = std::max(lmDamping * 0.1, 1e-12);
        } else {
            lmDamping = std::min(lmDamping * 10.0, 1e6);
        }

        std::cerr << "[CDS] iter=" << (iter+1)
                  << " alpha=" << bestAlpha
                  << " residual=" << currentResidual
                  << " -> " << computeTotalResidual()
                  << " lm=" << lmDamping << "\n";

        double newResidual = computeTotalResidual();
        if (newResidual < config_.tolerance) {
            report.result = SolverResult::Converged;
            report.finalResidual = newResidual;
            return report;
        }

        if (bestAlpha == 0.0 && iter > 5) {
            break;
        }
    }

    report.finalResidual = computeTotalResidual();
    if (report.finalResidual < config_.tolerance * 1000) {
        report.result = SolverResult::Converged;
    }

    return report;
}

}
}
