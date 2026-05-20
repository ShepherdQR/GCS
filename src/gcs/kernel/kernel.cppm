module;

#include <array>
#include <string>
#include <vector>

export module gcs.kernel;

export namespace gcs {

struct EntityId {
    int value = 0;
};

struct ConstraintId {
    int value = 0;
};

struct RigidSetId {
    int value = 0;
};

struct ContextId {
    int value = 0;
};

struct CoverId {
    int value = 0;
};

struct ProjectionId {
    int value = 0;
};

struct StateVersionId {
    int value = 0;
};

struct ReportId {
    int value = 0;
};

struct CommandId {
    int value = 0;
};

bool operator==(EntityId lhs, EntityId rhs);
bool operator==(ConstraintId lhs, ConstraintId rhs);
bool operator==(RigidSetId lhs, RigidSetId rhs);
bool operator==(ContextId lhs, ContextId rhs);
bool operator==(CoverId lhs, CoverId rhs);
bool operator==(ProjectionId lhs, ProjectionId rhs);
bool operator==(StateVersionId lhs, StateVersionId rhs);
bool operator==(ReportId lhs, ReportId rhs);
bool operator==(CommandId lhs, CommandId rhs);

enum class GeometryKind {
    Point = 0,
    Line = 1,
    Plane = 2,
};

enum class ConstraintKind {
    Coincident = 0,
    Parallel = 1,
    Perpendicular = 2,
    Distance = 3,
    Angle = 4,
};

enum class SolveMode {
    Update = 0,
    Drag = 1,
    Simulation = 2,
};

enum class ContextKind {
    WholeModel,
    ConnectedComponent,
    RigidSet,
    Subproblem,
    Overlap,
    Gauge,
};

enum class GaugeKind {
    None,
    AnchorEntities,
    QuotientRigidMotion,
};

enum class ReportSeverity {
    Info,
    Warning,
    Error,
};

enum class StageStatus {
    Ok,
    Warning,
    Error,
    Unsupported,
};

enum class SolveStatus {
    NotRun,
    Solved,
    AcceptedWithWarnings,
    InvalidModel,
    UnderConstrained,
    OverConstrained,
    Redundant,
    Inconsistent,
    NumericallySingular,
    Unsupported,
    Failed,
};

struct ParameterBlock {
    int dimension = 0;
    std::array<double, 6> values = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
};

struct EntityState {
    EntityId entityId;
    ParameterBlock parameters;
};

struct GeometricEntity {
    EntityId id;
    GeometryKind kind = GeometryKind::Point;
    RigidSetId rigidSetId;
    ParameterBlock parameters;
};

struct ConstraintInstance {
    ConstraintId id;
    ConstraintKind kind = ConstraintKind::Coincident;
    std::vector<EntityId> entityIds;
    double value = 0.0;
};

struct RigidSet {
    RigidSetId id;
    std::vector<EntityId> entityIds;
};

struct UnitsPolicy {
    std::string lengthUnit = "model";
    double lengthScale = 1.0;
};

struct TolerancePolicy {
    double residual = 1.0e-8;
    double rank = 1.0e-10;
    double boundary = 1.0e-8;
};

struct SolveIntent {
    SolveMode mode = SolveMode::Update;
    std::vector<EntityId> fixedEntityIds;
    std::vector<EntityId> drivenEntityIds;
    std::vector<ConstraintId> targetConstraintIds;
};

struct ModelSnapshot {
    std::string schemaVersion = "gcs-0.2";
    StateVersionId stateVersion;
    UnitsPolicy units;
    TolerancePolicy tolerances;
    SolveIntent solveIntent;
    std::vector<RigidSet> rigidSets;
    std::vector<GeometricEntity> entities;
    std::vector<ConstraintInstance> constraints;
};

struct ContextSnapshot {
    ContextId id;
    ContextKind kind = ContextKind::WholeModel;
    std::vector<EntityId> entityIds;
    std::vector<ConstraintId> constraintIds;
    std::vector<RigidSetId> rigidSetIds;
};

struct BoundaryProjection {
    ProjectionId id;
    ContextId sourceContextId;
    ContextId targetContextId;
    std::vector<EntityId> entityIds;
    std::vector<ConstraintId> constraintIds;
};

struct CoverPlan {
    CoverId id;
    ContextId rootContextId;
    std::vector<ContextSnapshot> contexts;
    std::vector<BoundaryProjection> boundaryProjections;
};

struct GaugePolicy {
    GaugeKind kind = GaugeKind::None;
    ContextId contextId;
    std::vector<EntityId> anchoredEntityIds;
    int removedDof = 0;
};

struct LocalSection {
    ContextId contextId;
    bool valid = false;
    std::vector<EntityState> entityStates;
};

struct ProposedState {
    StateVersionId baseVersion;
    std::vector<EntityState> entityStates;
};

struct ReportMessage {
    ReportSeverity severity = ReportSeverity::Info;
    std::string code;
    std::string message;
    std::vector<EntityId> entityIds;
    std::vector<ConstraintId> constraintIds;
    std::vector<ContextId> contextIds;
};

struct StageReport {
    ReportId id;
    std::string stage;
    StageStatus status = StageStatus::Ok;
    std::vector<ReportMessage> messages;
};

std::string toString(GeometryKind kind);
std::string toString(ConstraintKind kind);
std::string toString(SolveMode mode);
std::string toString(ContextKind kind);
std::string toString(GaugeKind kind);
std::string toString(SolveStatus status);
std::string toString(StageStatus status);

int geometryDof(GeometryKind kind);
int constraintDofEffect(ConstraintKind kind);

const GeometricEntity* findEntity(const ModelSnapshot& model, EntityId id);
const ConstraintInstance* findConstraint(const ModelSnapshot& model, ConstraintId id);
const RigidSet* findRigidSet(const ModelSnapshot& model, RigidSetId id);

bool containsEntity(const std::vector<EntityId>& ids, EntityId id);
bool containsConstraint(const std::vector<ConstraintId>& ids, ConstraintId id);
bool containsRigidSet(const std::vector<RigidSetId>& ids, RigidSetId id);

ContextSnapshot makeWholeModelContext(const ModelSnapshot& model, ContextId id = ContextId{0});
std::vector<EntityState> captureEntityStates(const ModelSnapshot& model,
                                             const std::vector<EntityId>& entityIds);
StateVersionId nextVersion(StateVersionId current);
StageReport makeStageReport(std::string stage, StageStatus status = StageStatus::Ok);

}
