#pragma once

namespace gcs {

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

}
