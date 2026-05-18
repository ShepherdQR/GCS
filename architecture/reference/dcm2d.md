# D-Cubed 2D DCM Reference Architecture

## Product Boundary

D-Cubed 2D DCM is Siemens' 2D Dimensional Constraint Manager. Public material positions it as a widely adopted 2D sketch constraint solver for CAD/CAM/CAE applications. It supports sketch creation and modification through dimensions and geometric constraints, including automatic inference during drawing or from legacy drawings.

Sources:

- Siemens D-Cubed 2D DCM product page: https://www.siemens.com/en-gb/products/plm-components/d-cubed/2d-dcm/
- Siemens PLM Components introduction to geometric constraint solving: https://blogs.sw.siemens.com/plm-components/geometric-constraint-solving-1-introduction/

## Key Design

2D DCM is a sketch solver. Its public architecture surface is optimized for fast interactive loops:

- Sketch entities: points, lines, circles, ellipses, conics, splines, parametric curves.
- Constraint families: distance, angle, radius, parallel, perpendicular, tangent, concentric, symmetric, normal, equal distance, equal radius.
- Equation linkage: variable dimensions can be connected through equations and solved together.
- Inference: constraints can be inferred from existing drawings or while users sketch.
- Free-form support: spline length, tangent direction, tangent length, second derivative, equal direction, equal curvature.
- Solve behavior: solving modes can prefer outcomes such as minimal geometry movement.
- Diagnostics: always returns feedback for under-constrained and over-constrained sketches.

The important design point is that 2D DCM is not just "Newton on equations." It combines constraint inference, behavior preferences, curve-specific constraint handling, equation solving, and diagnostic feedback around an interactive sketch session.

## Design Lessons For Us

Do not merge UI gestures directly into numeric solving. Dragging, minimum-motion preferences, and inferred constraints belong to behavior intent. Numeric solving should receive them as input.

Keep 2D-specific logic optional. Our current project is mostly 3D/minimal. A future 2D sketch solver can share structural concepts but should be allowed to specialize its entities, signatures, inference, and solving heuristics.

Represent "natural movement" explicitly. For interactive demonstrations, moving the smallest meaningful part of the graph matters more than exposing every numeric residual.

## What We Should Not Copy Yet

Do not implement auto-constraining, spline constraints, equation networks, or a full sketcher now. The useful near-term borrowing is the update/drag behavior model and diagnostic loop.

