# D-Cubed 3D DCM Reference Architecture

## Product Boundary

D-Cubed 3D DCM is Siemens' 3D Dimensional Constraint Manager. Public material positions it as a 3D geometric constraint solver for assembly constraints, kinematic simulation, direct modeling, and 3D sketching.

Sources:

- Siemens D-Cubed 3D DCM product page: https://www.siemens.com/en-us/products/plm-components/d-cubed/3d-dcm/
- Siemens D-Cubed 3D components release highlights: https://blogs.sw.siemens.com/plm-components/d-cubed-3d-components-release-highlights/

## Key Design

3D DCM is centered on positioning and motion of 3D parts while preserving design intent:

- Application domains: assembly positioning, kinematic simulation, direct modeling, 3D sketches, routes for pipes and wires.
- Geometry coverage: points, lines, planes, circles, ellipses, cylinders, tori, parametric curves, and surfaces.
- Constraint families: distance, angle, radius, parallel, perpendicular, tangent, concentric, symmetric, normal, midpoint, pattern, bounded dimensions.
- Equations: variable dimensions can be linked to drive kinematics or related motion.
- Free-form geometry: rigid bodies can be constrained against free-form curves and surfaces.
- Solving behavior: modes can prefer moving the fewest geometries or moving geometry the minimum amount.
- Diagnostics: feedback for well-defined, under-defined, and over-defined model status.
- Rigid sets: geometry can be grouped into sets that define rigid 3D parts; constraints position the set without changing its internal shape.
- DOF feedback: 3D parts normally have six rigid-body degrees of freedom, with special handling for symmetries.

The major architectural distinction from 2D DCM is that 3D assemblies require rigid-body transforms and DOF diagnostics around sets, not only raw geometry parameters.

## Design Lessons For Us

Make `RigidSet` first-class. A rigid set should eventually carry a transform and be diagnosed as a body. Constraints should position rigid sets or their exposed geometry without accidentally deforming the set.

Separate internal geometry from assembly behavior. A part's internal structure can be stable while its set transform changes. This should be visible in both the C++ model and the lightweight graph visualization.

Report DOF at the right level. Raw geometry DOF is useful for debugging, but assembly users need rigid-set DOF, removed DOF, unresolved DOF, and over-definition status.

## What We Should Not Copy Yet

Do not implement full surface/curve coverage, symmetry-aware DOF, kinematics, or bounded dimensions yet. Preserve the architecture slots and build only point/line/plane examples until the graph behavior is stable.

