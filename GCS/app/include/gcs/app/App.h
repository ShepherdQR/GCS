#pragma once

#include "gcs/core/core.h"
#include "gcs/dcm/dcm.h"
#include "gcs/lgs/lgs.h"
#include "gcs/cds/cds.h"
#include "gcs/io/io.h"
#include <array>
#include <memory>
#include <unordered_map>

namespace gcs {
namespace app {

struct IGeometry {
    virtual ~IGeometry() = default;
    virtual int id() const = 0;
    virtual GeometryType type() const = 0;
    virtual int rigidSetId() const = 0;
    virtual std::array<double, 6> parameters() const = 0;
};

struct IConstraint {
    virtual ~IConstraint() = default;
    virtual int id() const = 0;
    virtual ConstraintType type() const = 0;
    virtual const std::vector<int>& geometryIds() const = 0;
    virtual double value() const = 0;
};

struct IRigidSet {
    virtual ~IRigidSet() = default;
    virtual int id() const = 0;
    virtual const std::vector<int>& geometryIds() const = 0;
};

struct IProblem {
    virtual ~IProblem() = default;
    virtual const std::vector<std::unique_ptr<IRigidSet>>& rigidSets() const = 0;
    virtual const std::vector<std::unique_ptr<IGeometry>>& geometries() const = 0;
    virtual const std::vector<std::unique_ptr<IConstraint>>& constraints() const = 0;
};

void translateProblem(const IProblem& problem, Manager& m);

class App {
public:
    static App& instance();

    App& addRigidSet(int id);
    App& addGeometry(int id, GeometryType type, int rigidSetId,
                     const std::array<double, 6>& params = {0,0,0,0,0,0});
    App& addConstraint(int id, ConstraintType type,
                       const std::vector<int>& geomIds, double value = 0.0);

    App& loadProblem(const IProblem& problem);
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

} // namespace app
} // namespace gcs
