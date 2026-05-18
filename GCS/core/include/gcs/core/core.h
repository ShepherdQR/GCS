#pragma once

#include "types.h"
#include <vector>
#include <string>

namespace gcs {

struct RigidSet {
    int id;
    std::vector<int> geometryIds;
};

struct Geometry {
    int id;
    GeometryType type;
    int rigidSetId;
    double v[6];
};

struct Constraint {
    int id;
    ConstraintType type;
    std::vector<int> geometryIds;
    double value;
};

struct HistoryAction {
    std::string action;
    std::string payload;
};

struct Manager {
    std::vector<RigidSet> rigidSets;
    std::vector<Geometry> geometries;
    std::vector<Constraint> constraints;
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
int dofGeometry(GeometryType t);
int dofRemovedConstraint(ConstraintType t);

}
