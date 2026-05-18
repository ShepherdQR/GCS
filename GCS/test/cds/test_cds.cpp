#include "test_framework.h"
#include "gcs/cds/cds.h"
#include "gcs/dcm/dcm.h"
#include "gcs/lgs/lgs.h"

using namespace gcs;

static Manager makeUnderConstrainedProblem() {
    Manager m;
    RigidSet rs; rs.id = 0; rs.geometryIds = {0, 1};
    m.rigidSets.push_back(rs);
    Geometry g0; g0.id = 0; g0.type = GeometryType::Point; g0.rigidSetId = 0;
    Geometry g1; g1.id = 1; g1.type = GeometryType::Point; g1.rigidSetId = 0;
    for (int i = 0; i < 6; ++i) { g0.v[i] = 0; g1.v[i] = 0; }
    g1.v[0] = 5;
    m.geometries.push_back(g0);
    m.geometries.push_back(g1);
    Constraint c; c.id = 0; c.type = ConstraintType::Distance; c.geometryIds = {0, 1}; c.value = 3;
    m.constraints.push_back(c);
    return m;
}

void test_cds_solve_returns_report() {
    auto m = makeUnderConstrainedProblem();
    cds::ConstraintDrivenSolver solver;
    auto report = solver.solve(m);
    bool valid = (report.result == cds::SolverResult::Converged ||
                  report.result == cds::SolverResult::Diverged ||
                  report.result == cds::SolverResult::MaxIterationsReached ||
                  report.result == cds::SolverResult::SingularJacobian ||
                  report.result == cds::SolverResult::InconsistentConstraints);
    GCS_ASSERT(valid, "CD01: solve returns valid result enum");
}

void test_cds_solve_subproblem_returns_report() {
    auto m = makeUnderConstrainedProblem();
    dcm::DecompositionManager dcm;
    auto decomp = dcm.decompose(m);
    cds::ConstraintDrivenSolver solver;
    if (!decomp.subProblems.empty()) {
        auto report = solver.solveSubProblem(m, decomp.subProblems[0]);
        bool valid = (report.result == cds::SolverResult::Converged ||
                      report.result == cds::SolverResult::Diverged ||
                      report.result == cds::SolverResult::MaxIterationsReached ||
                      report.result == cds::SolverResult::SingularJacobian ||
                      report.result == cds::SolverResult::InconsistentConstraints);
        GCS_ASSERT(valid, "CD02: solveSubProblem returns valid result enum");
    } else {
        GCS_ASSERT(false, "CD02: expected at least 1 sub-problem");
    }
}

void test_cds_solve_under_constrained() {
    auto m = makeUnderConstrainedProblem();
    dcm::DecompositionManager dcm;
    auto decomp = dcm.decompose(m);
    cds::ConstraintDrivenSolver solver;
    if (!decomp.subProblems.empty()) {
        auto report = solver.solveSubProblem(m, decomp.subProblems[0]);
        bool isExpected = (report.result == cds::SolverResult::InconsistentConstraints ||
                           report.result == cds::SolverResult::MaxIterationsReached);
        GCS_ASSERT(isExpected, "CD03: under-constrained returns InconsistentConstraints or MaxIterationsReached");
    } else {
        GCS_ASSERT(false, "CD03: expected at least 1 sub-problem");
    }
}

void test_cds_report_iterations() {
    auto m = makeUnderConstrainedProblem();
    dcm::DecompositionManager dcm;
    auto decomp = dcm.decompose(m);
    cds::ConstraintDrivenSolver solver;
    if (!decomp.subProblems.empty()) {
        auto report = solver.solveSubProblem(m, decomp.subProblems[0]);
        GCS_ASSERT_GE(report.iterationsUsed, 0, "CD04: iterationsUsed >= 0");
    } else {
        GCS_ASSERT(false, "CD04: expected at least 1 sub-problem");
    }
}

void test_cds_report_residuals() {
    auto m = makeUnderConstrainedProblem();
    dcm::DecompositionManager dcm;
    auto decomp = dcm.decompose(m);
    cds::ConstraintDrivenSolver solver;
    if (!decomp.subProblems.empty()) {
        auto report = solver.solveSubProblem(m, decomp.subProblems[0]);
        GCS_ASSERT_GE(report.initialResidual, 0.0, "CD05: initialResidual >= 0");
        GCS_ASSERT_GE(report.finalResidual, 0.0, "CD05: finalResidual >= 0");
    } else {
        GCS_ASSERT(false, "CD05: expected at least 1 sub-problem");
    }
}

void test_cds_config_default() {
    cds::SolverConfig config;
    GCS_ASSERT_EQ(config.maxIterations, 100, "CD06: default maxIterations=100");
    GCS_ASSERT_NEAR(config.tolerance, 1e-8, 1e-15, "CD06: default tolerance=1e-8");
    GCS_ASSERT_NEAR(config.dampingFactor, 1.0, 1e-15, "CD06: default dampingFactor=1.0");
}

void test_cds_config_custom() {
    cds::SolverConfig config;
    config.maxIterations = 50;
    config.tolerance = 1e-6;
    cds::ConstraintDrivenSolver solver(config);
    solver.setConfig(config);
    GCS_ASSERT_EQ(solver.config().maxIterations, 50, "CD07: custom maxIterations=50");
    GCS_ASSERT_NEAR(solver.config().tolerance, 1e-6, 1e-15, "CD07: custom tolerance=1e-6");
}

void test_cds_config_affects_solve() {
    auto m = makeUnderConstrainedProblem();
    cds::SolverConfig config;
    config.maxIterations = 1;
    cds::ConstraintDrivenSolver solver(config);
    auto report = solver.solve(m);
    GCS_ASSERT_LE(report.iterationsUsed, 1, "CD08: maxIterations=1 limits iterations");
}

void test_cds_result_to_string() {
    GCS_ASSERT(!cds::toString(cds::SolverResult::Converged).empty(), "CD09: Converged toString");
    GCS_ASSERT(!cds::toString(cds::SolverResult::Diverged).empty(), "CD09: Diverged toString");
    GCS_ASSERT(!cds::toString(cds::SolverResult::MaxIterationsReached).empty(), "CD09: MaxIterationsReached toString");
    GCS_ASSERT(!cds::toString(cds::SolverResult::SingularJacobian).empty(), "CD09: SingularJacobian toString");
    GCS_ASSERT(!cds::toString(cds::SolverResult::InconsistentConstraints).empty(), "CD09: InconsistentConstraints toString");
}

void test_cds_solve_empty_manager() {
    Manager m;
    cds::ConstraintDrivenSolver solver;
    auto report = solver.solve(m);
    GCS_ASSERT(true, "CD10: solve empty Manager no crash");
}

int main() {
    std::cout << "=== CDS Interface Tests ===\n\n";

    test_cds_solve_returns_report();
    test_cds_solve_subproblem_returns_report();
    test_cds_solve_under_constrained();
    test_cds_report_iterations();
    test_cds_report_residuals();
    test_cds_config_default();
    test_cds_config_custom();
    test_cds_config_affects_solve();
    test_cds_result_to_string();
    test_cds_solve_empty_manager();

    GCS_TEST_SUMMARY();
}
