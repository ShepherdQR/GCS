module;

#include <array>
#include <string>
#include <unordered_map>
#include <vector>

export module gcs.app;

export import gcs.core;
export import gcs.dcm;
export import gcs.lgs;
export import gcs.cds;
export import gcs.io;

export namespace gcs::app {

class App {
public:
    static App& instance();

    App& addRigidSet(int id);
    App& addGeometry(int id, GeometryType type, int rigidSetId,
                     const std::array<double, 6>& params = {0, 0, 0, 0, 0, 0});
    App& addConstraint(int id, ConstraintType type,
                       const std::vector<int>& geomIds, double value = 0.0);

    App& loadFile(const std::string& path);

    App& compute();

    const std::array<double, 6>& getTransformation(int rigidSetId) const;
    const Manager& manager() const;
    const dcm::DecompositionResult& decomposition() const;
    const lgs::StatusReport& globalStatus() const;
    const std::vector<cds::SolverReport>& solverReports() const;

    App& reset();

private:
    App() = default;
    Manager manager_;
    dcm::DecompositionResult decomp_;
    lgs::StatusReport globalStatus_;
    std::vector<cds::SolverReport> solverReports_;
    std::unordered_map<int, std::array<double, 6>> transformations_;
    bool computed_ = false;
    static std::array<double, 6> zero_params_;
};

}
