module;

#include <algorithm>
#include <string>
#include <vector>

module gcs.kernel;

namespace gcs {

RigidSet* Manager::findRigidSet(int id) {
    for (auto& rs : rigidSets) if (rs.id == id) return &rs;
    return nullptr;
}

const RigidSet* Manager::findRigidSet(int id) const {
    for (auto& rs : rigidSets) if (rs.id == id) return &rs;
    return nullptr;
}

Geometry* Manager::findGeometry(int id) {
    for (auto& g : geometries) if (g.id == id) return &g;
    return nullptr;
}

const Geometry* Manager::findGeometry(int id) const {
    for (auto& g : geometries) if (g.id == id) return &g;
    return nullptr;
}

Constraint* Manager::findConstraint(int id) {
    for (auto& c : constraints) if (c.id == id) return &c;
    return nullptr;
}

const Constraint* Manager::findConstraint(int id) const {
    for (auto& c : constraints) if (c.id == id) return &c;
    return nullptr;
}

std::string typeNameGeometry(GeometryType t) {
    switch (t) {
        case GeometryType::Point:   return "Point";
        case GeometryType::Line:    return "Line";
        case GeometryType::Plane:   return "Plane";
    }
    return "Unknown";
}

std::string typeNameConstraint(ConstraintType t) {
    switch (t) {
        case ConstraintType::Coincident:    return "Coincident";
        case ConstraintType::Parallel:      return "Parallel";
        case ConstraintType::Perpendicular: return "Perpendicular";
        case ConstraintType::Distance:      return "Distance";
        case ConstraintType::Angle:         return "Angle";
    }
    return "Unknown";
}

std::string typeNameSolveMode(SolveMode t) {
    switch (t) {
        case SolveMode::Update:     return "Update";
        case SolveMode::Drag:       return "Drag";
        case SolveMode::Simulation: return "Simulation";
    }
    return "Unknown";
}

int dofGeometry(GeometryType t) {
    switch (t) {
        case GeometryType::Point: return 3;
        case GeometryType::Line:  return 6;
        case GeometryType::Plane: return 6;
    }
    return 0;
}

int dofRemovedConstraint(ConstraintType t) {
    switch (t) {
        case ConstraintType::Coincident:    return 3;
        case ConstraintType::Parallel:      return 2;
        case ConstraintType::Perpendicular: return 1;
        case ConstraintType::Distance:      return 1;
        case ConstraintType::Angle:         return 1;
    }
    return 0;
}

}
