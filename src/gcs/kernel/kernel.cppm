module;

#include <array>
#include <cstdint>
#include <string>
#include <vector>

export module gcs.kernel;

export namespace gcs::kernel {

struct EntityId {
    std::uint64_t value = 0;
    friend bool operator==(EntityId, EntityId) = default;
};

struct ConstraintId {
    std::uint64_t value = 0;
    friend bool operator==(ConstraintId, ConstraintId) = default;
};

struct RigidSetId {
    std::uint64_t value = 0;
    friend bool operator==(RigidSetId, RigidSetId) = default;
};

struct ContextId {
    std::uint64_t value = 0;
    friend bool operator==(ContextId, ContextId) = default;
};

struct StateVersionId {
    std::uint64_t value = 0;
    friend bool operator==(StateVersionId, StateVersionId) = default;
};

struct ReportId {
    std::uint64_t value = 0;
    friend bool operator==(ReportId, ReportId) = default;
};

enum class GeometryKind {
    point,
    line,
    plane,
};

enum class ConstraintKind {
    coincident,
    parallel,
    perpendicular,
    distance,
    angle,
};

enum class ContextKind {
    whole_model,
    connected_component,
    rigid_set,
    subproblem,
    overlap,
    gauge,
};

enum class ReportSeverity {
    info,
    warning,
    error,
};

enum class StageStatus {
    ok,
    warning,
    error,
    unsupported,
};

struct StableId {
    std::string domain;
    std::uint64_t value = 0;
    friend bool operator==(const StableId&, const StableId&) = default;
};

struct ReportCode {
    std::string value;
    friend bool operator==(const ReportCode&, const ReportCode&) = default;
};

struct ReportMessage {
    ReportSeverity severity = ReportSeverity::info;
    ReportCode code;
    std::string summary;
    std::vector<StableId> subjects;
};

struct StageReport {
    ReportId report_id;
    std::string stage;
    StageStatus status = StageStatus::ok;
    std::vector<ReportMessage> messages;
};

template <class Payload>
struct ContractResult {
    Payload payload;
    StageReport report;
};

struct ParameterVector {
    int dimension = 0;
    std::array<double, 6> values = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
    friend bool operator==(const ParameterVector&, const ParameterVector&) = default;
};

struct EntityDraft {
    EntityId id;
    GeometryKind kind = GeometryKind::point;
    RigidSetId rigid_set_id;
    ParameterVector parameters;
};

struct ConstraintDraft {
    ConstraintId id;
    ConstraintKind kind = ConstraintKind::coincident;
    std::vector<EntityId> entity_ids;
    double value = 0.0;
};

struct RigidSetDraft {
    RigidSetId id;
    std::vector<EntityId> entity_ids;
};

struct UnitsPolicy {
    std::string length_unit = "model";
    double length_scale = 1.0;
};

struct TolerancePolicy {
    double residual = 1.0e-8;
    double rank = 1.0e-10;
    double boundary = 1.0e-8;
};

struct EntityState {
    EntityId entity_id;
    ParameterVector parameters;
};

struct ModelDraft {
    std::string schema_version = "gcs-0.3";
    StateVersionId initial_state_version;
    UnitsPolicy units;
    TolerancePolicy tolerances;
    std::vector<RigidSetDraft> rigid_sets;
    std::vector<EntityDraft> entities;
    std::vector<ConstraintDraft> constraints;
};

struct ModelSnapshot {
    std::string schema_version = "gcs-0.3";
    StateVersionId state_version;
    UnitsPolicy units;
    TolerancePolicy tolerances;
    std::vector<RigidSetDraft> rigid_sets;
    std::vector<EntityDraft> entities;
    std::vector<ConstraintDraft> constraints;
};

struct ContextRequest {
    ContextId id;
    ContextKind kind = ContextKind::whole_model;
    std::vector<EntityId> entity_ids;
    std::vector<ConstraintId> constraint_ids;
    std::vector<RigidSetId> rigid_set_ids;
};

struct ContextSnapshot {
    ContextId id;
    ContextKind kind = ContextKind::whole_model;
    StateVersionId state_version;
    std::vector<EntityId> entity_ids;
    std::vector<ConstraintId> constraint_ids;
    std::vector<RigidSetId> rigid_set_ids;
};

struct StateDelta {
    StateVersionId base_version;
    StateVersionId target_version;
    std::vector<EntityState> entity_states;
};

struct SnapshotDiffRequest {
    ModelSnapshot before;
    ModelSnapshot after;
};

struct ModelValidationReport {
    bool valid = true;
    int entity_count = 0;
    int constraint_count = 0;
    int rigid_set_count = 0;
};

struct ContextValidationReport {
    bool valid = true;
    bool covers_whole_model = false;
};

struct SnapshotDiff {
    bool same_schema = true;
    bool state_version_changed = false;
    std::vector<EntityId> added_entities;
    std::vector<EntityId> removed_entities;
    std::vector<EntityId> changed_entities;
    std::vector<ConstraintId> added_constraints;
    std::vector<ConstraintId> removed_constraints;
};

struct StateDeltaValidationReport {
    bool valid = true;
    bool base_version_matches = true;
    bool target_version_is_next = true;
};

int geometry_dof(GeometryKind kind);
StateVersionId next_version(StateVersionId current);
ContractResult<ModelSnapshot> make_snapshot(ModelDraft draft);
ContractResult<ModelValidationReport> validate_model(const ModelSnapshot& snapshot);
ContractResult<ContextSnapshot> make_context(const ModelSnapshot& snapshot,
                                             ContextRequest request);
ContractResult<ContextValidationReport> validate_context(const ModelSnapshot& snapshot,
                                                         const ContextSnapshot& context);
ContractResult<SnapshotDiff> diff_snapshots(const ModelSnapshot& before,
                                            const ModelSnapshot& after);
ContractResult<StateDeltaValidationReport> validate_delta(const ModelSnapshot& base,
                                                          const StateDelta& delta);

}

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
