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

struct CoverId {
    std::uint64_t value = 0;
    friend bool operator==(CoverId, CoverId) = default;
};

struct ProjectionId {
    std::uint64_t value = 0;
    friend bool operator==(ProjectionId, ProjectionId) = default;
};

struct StateVersionId {
    std::uint64_t value = 0;
    friend bool operator==(StateVersionId, StateVersionId) = default;
};

struct ReportId {
    std::uint64_t value = 0;
    friend bool operator==(ReportId, ReportId) = default;
};

struct CommandId {
    std::uint64_t value = 0;
    friend bool operator==(CommandId, CommandId) = default;
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

enum class SolveMode {
    update,
    drag,
    simulation,
};

enum class ContextKind {
    whole_model,
    connected_component,
    rigid_set,
    subproblem,
    overlap,
    gauge,
};

enum class GaugeKind {
    none,
    anchor_entities,
    quotient_rigid_motion,
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

enum class SolveStatus {
    not_run,
    solved,
    accepted_with_warnings,
    invalid_model,
    under_constrained,
    over_constrained,
    redundant,
    inconsistent,
    numerically_singular,
    unsupported,
    failed,
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

struct SolveIntent {
    SolveMode mode = SolveMode::update;
    std::vector<EntityId> fixed_entity_ids;
    std::vector<EntityId> driven_entity_ids;
    std::vector<ConstraintId> target_constraint_ids;
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
    SolveIntent solve_intent;
    std::vector<RigidSetDraft> rigid_sets;
    std::vector<EntityDraft> entities;
    std::vector<ConstraintDraft> constraints;
};

struct ModelSnapshot {
    std::string schema_version = "gcs-0.3";
    StateVersionId state_version;
    UnitsPolicy units;
    TolerancePolicy tolerances;
    SolveIntent solve_intent;
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

struct BoundaryProjection {
    ProjectionId id;
    ContextId source_context_id;
    ContextId target_context_id;
    std::vector<EntityId> entity_ids;
    std::vector<ConstraintId> constraint_ids;
};

struct CoverPlan {
    CoverId id;
    ContextId root_context_id;
    std::vector<ContextSnapshot> contexts;
    std::vector<BoundaryProjection> boundary_projections;
};

struct GaugePolicy {
    GaugeKind kind = GaugeKind::none;
    ContextId context_id;
    std::vector<EntityId> anchored_entity_ids;
    int removed_dof = 0;
};

struct LocalSection {
    ContextId context_id;
    bool valid = false;
    std::vector<EntityState> entity_states;
};

struct ProposedState {
    StateVersionId base_version;
    std::vector<EntityState> entity_states;
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

std::string to_string(GeometryKind kind);
std::string to_string(ConstraintKind kind);
std::string to_string(SolveMode mode);
std::string to_string(ContextKind kind);
std::string to_string(GaugeKind kind);
std::string to_string(SolveStatus status);
std::string to_string(StageStatus status);

int geometry_dof(GeometryKind kind);
int constraint_dof_effect(ConstraintKind kind);

const EntityDraft* find_entity(const ModelSnapshot& snapshot, EntityId id);
const ConstraintDraft* find_constraint(const ModelSnapshot& snapshot, ConstraintId id);
const RigidSetDraft* find_rigid_set(const ModelSnapshot& snapshot, RigidSetId id);

bool contains_entity(const std::vector<EntityId>& ids, EntityId id);
bool contains_constraint(const std::vector<ConstraintId>& ids, ConstraintId id);
bool contains_rigid_set(const std::vector<RigidSetId>& ids, RigidSetId id);
bool has_errors(const StageReport& report);

StageReport make_stage_report(std::string stage, StageStatus status = StageStatus::ok);
ReportMessage make_report_message(ReportSeverity severity,
                                  ReportCode code,
                                  std::string summary,
                                  std::vector<StableId> subjects = {});
void append_report_message(StageReport& report, ReportMessage message);

StateVersionId next_version(StateVersionId current);
ContextSnapshot make_whole_model_context(const ModelSnapshot& snapshot,
                                         ContextId id = ContextId{0});
std::vector<EntityState> capture_entity_states(const ModelSnapshot& snapshot,
                                               const std::vector<EntityId>& entity_ids);

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
