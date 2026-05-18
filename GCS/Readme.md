

# GCS

## step1 class description

class RigidSet: // RS
 id: int // unique identifier, the index of the rigid set in the rigid set list

class Geometry: // G
 id: int // the index of the geometry in the geometry list
 value: double[6] // for point: x, y, z, 0, 0, 0; for line: x1, y1, z1, x2, y2, z2; for plane: x, y, z, nx, ny, nz

class Constriant: // C
 id: int // the index of the constraint in the constraint list
 value: double // for distance: the distance value; for angle: the angle value in degree, otherwise 0

type of Geometry:
- Point:0
- Line:1
- Plane:2

type of Constriant:
- Coincident:0
- Parallel:1
- Perpendicular:2
- Distance:3
- Angle:4

class Manager:
- RigidSet* rigidSetList
- Geometry* geometryList
- Constraint* constraintList

## step2 class relationship

1 RS contains multiple G
1 C connects multiple G

## step3 serialization structure
// we define one GCS graph as a list of RigidSet, Geometry and Constraint
// 1. the topology of the GCS graph is defined by the relationship between RigidSet, Geometry and Constraint
numOfRigidSet
idOfRigidSet1, idOfRigidSet2, ...
numOfGeometry
idOfGeometry1, type of geometry, id of the the rigid set it belongs to,  ...
idOfGeometry2, type of geometry, id of the the rigid set it belongs to, ...
...
numOfConstraint
idOfConstraint1, type of constraint, id of the geometry it connects, ...
idOfConstraint2, type of constraint, id of the geometry it connects, ...
...
// 2. the parameters of the GCS graph
idofGeometry1, value of geometry
idofGeometry2, value of geometry
...
idofConstraint1, value of constraint
idofConstraint2, value of constraint
...
// end.








