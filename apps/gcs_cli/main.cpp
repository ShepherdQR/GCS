import gcs.session_runtime;

#include <cstddef>
#include <iostream>
#include <string>

using namespace gcs;
using namespace gcs::app;

int main(int argc, char** argv) {
    std::string path = "fixtures/scene/basic/g1.txt";
    if (argc > 1) path = argv[1];

    App::instance().loadFile(path).compute();

    auto& m = App::instance().manager();
    std::cout << "GCS Graph loaded from: " << path << "\n";
    io::printSummary(m);

    auto& decomp = App::instance().decomposition();
    std::cout << "\nDecomposed into " << decomp.subProblems.size() << " sub-problem(s)\n";

    lgs::LocalGeometricSolver lgs;
    for (const auto& sp : decomp.subProblems) {
        auto status = lgs.analyzeStatus(m, sp);
        std::cout << "  Sub-problem " << sp.id
                  << ": " << sp.geometryIds.size() << " geometries, "
                  << sp.constraintIds.size() << " constraints, "
                  << lgs::toString(status.overallStatus)
                  << " (net DOF=" << status.dofAnalysis.netDOF << ")\n";
    }

    auto& globalStatus = App::instance().globalStatus();
    std::cout << "\nGlobal status: " << lgs::toString(globalStatus.overallStatus)
              << " (net DOF=" << globalStatus.dofAnalysis.netDOF << ")\n";

    auto& reports = App::instance().solverReports();
    for (size_t i = 0; i < reports.size(); i++) {
        const auto& report = reports[i];
        std::cout << "Solver sub-problem " << i << ": " << cds::toString(report.result)
                  << " in " << report.iterationsUsed << " iterations"
                  << " (residual: " << report.initialResidual
                  << " -> " << report.finalResidual << ")\n";
    }

    std::cout << "\n--- Constraint Satisfaction Check ---\n";
    auto violations = lgs.checkSatisfaction(m, 1e-6);
    bool allSatisfied = true;
    for (const auto& v : violations) {
        const auto* c = m.findConstraint(v.constraintId);
        std::string cType = c ? typeNameConstraint(c->type) : "?";
        std::string status = v.satisfied ? "SATISFIED" : "VIOLATED";
        std::cout << "  C" << v.constraintId << " (" << cType << ")"
                  << " residual=" << v.residual
                  << " tolerance=" << v.tolerance
                  << " " << status << "\n";
        if (!v.satisfied) allSatisfied = false;
    }
    if (allSatisfied) {
        std::cout << "  >>> All constraints satisfied <<<\n";
    } else {
        std::cout << "  >>> Some constraints VIOLATED <<<\n";
    }

    std::cout << "\n--- Geometry Coordinates ---\n";
    for (const auto& g : m.geometries) {
        std::cout << "  G" << g.id << " (" << typeNameGeometry(g.type) << ")"
                  << " RS" << g.rigidSetId
                  << " pos=(" << g.v[0] << "," << g.v[1] << "," << g.v[2] << ")";
        if (g.type == GeometryType::Line) {
            std::cout << " dir=(" << g.v[3] << "," << g.v[4] << "," << g.v[5] << ")";
        }
        std::cout << "\n";
    }

    bool isJson = path.size() >= 5 && path.substr(path.size() - 5) == ".json";
    if (isJson) {
        io::dumpGraphJSON(m, path);
    } else {
        io::dumpGraph(m, path);
    }

    App::instance().reset();
    return 0;
}
