module;

#include <string>
#include <vector>

export module gcs.kernel;

export namespace gcs {

enum class GeometryType {
    Point = 0,
    Line = 1,
    Plane = 2
};

enum class ConstraintType {
    Coincident = 0,
    Parallel = 1,
    Perpendicular = 2,
    Distance = 3,
    Angle = 4
};

enum class SolveMode {
    Update = 0,
    Drag = 1,
    Simulation = 2
};

struct RigidSet {
    int id = 0;
    std::vector<int> geometryIds;
};

struct Geometry {
    int id = 0;
    GeometryType type = GeometryType::Point;
    int rigidSetId = 0;
    double v[6] = {};
};

struct Constraint {
    int id = 0;
    ConstraintType type = ConstraintType::Coincident;
    std::vector<int> geometryIds;
    double value = 0.0;
};

struct BehaviorModel {
    SolveMode mode = SolveMode::Update;
    std::vector<int> fixedGeometryIds;
    std::vector<int> drivenGeometryIds;
    std::vector<int> targetConstraintIds;
};

struct HistoryAction {
    std::string action;
    std::string payload;
};

struct Manager {
    std::vector<RigidSet> rigidSets;
    std::vector<Geometry> geometries;
    std::vector<Constraint> constraints;
    BehaviorModel behavior;
    std::vector<HistoryAction> history;

    RigidSet* findRigidSet(int id);
    const RigidSet* findRigidSet(int id) const;
    Geometry* findGeometry(int id);
    const Geometry* findGeometry(int id) const;
    Constraint* findConstraint(int id);
    const Constraint* findConstraint(int id) const;
};

std::string typeNameGeometry(GeometryType t);
std::string typeNameConstraint(ConstraintType t);
std::string typeNameSolveMode(SolveMode t);
int dofGeometry(GeometryType t);
int dofRemovedConstraint(ConstraintType t);

}
