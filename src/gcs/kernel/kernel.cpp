module;

#include <algorithm>
#include <cstdint>
#include <string>
#include <utility>
#include <vector>

module gcs.kernel;

namespace gcs::kernel {

namespace {

constexpr const char* entity_domain = "entity";
constexpr const char* constraint_domain = "constraint";
constexpr const char* rigid_set_domain = "rigid_set";
constexpr const char* state_version_domain = "state_version";

ReportCode code(std::string value) {
    return ReportCode{std::move(value)};
}

StableId subject(const char* domain, std::uint64_t value) {
    return StableId{domain, value};
}

StageReport make_report(std::string stage) {
    StageReport report;
    report.stage = std::move(stage);
    return report;
}

void append_message(StageReport& report,
                    ReportSeverity severity,
                    ReportCode report_code,
                    std::string summary,
                    std::vector<StableId> subjects = {}) {
    if (severity == ReportSeverity::error) {
        report.status = StageStatus::error;
    } else if (severity == ReportSeverity::warning && report.status == StageStatus::ok) {
        report.status = StageStatus::warning;
    }

    ReportMessage message;
    message.severity = severity;
    message.code = std::move(report_code);
    message.summary = std::move(summary);
    message.subjects = std::move(subjects);
    report.messages.push_back(std::move(message));
}

bool has_errors(const StageReport& report) {
    if (report.status == StageStatus::error) return true;
    for (const auto& message : report.messages) {
        if (message.severity == ReportSeverity::error) return true;
    }
    return false;
}

bool contains_entity_id(const std::vector<EntityId>& ids, EntityId id) {
    return std::find(ids.begin(), ids.end(), id) != ids.end();
}

bool contains_constraint_id(const std::vector<ConstraintId>& ids, ConstraintId id) {
    return std::find(ids.begin(), ids.end(), id) != ids.end();
}

bool contains_rigid_set_id(const std::vector<RigidSetId>& ids, RigidSetId id) {
    return std::find(ids.begin(), ids.end(), id) != ids.end();
}

const EntityDraft* find_entity(const ModelSnapshot& snapshot, EntityId id) {
    for (const auto& entity : snapshot.entities) {
        if (entity.id == id) return &entity;
    }
    return nullptr;
}

const ConstraintDraft* find_constraint(const ModelSnapshot& snapshot, ConstraintId id) {
    for (const auto& constraint : snapshot.constraints) {
        if (constraint.id == id) return &constraint;
    }
    return nullptr;
}

const RigidSetDraft* find_rigid_set(const ModelSnapshot& snapshot, RigidSetId id) {
    for (const auto& rigid_set : snapshot.rigid_sets) {
        if (rigid_set.id == id) return &rigid_set;
    }
    return nullptr;
}

template <class Id>
bool already_seen(const std::vector<Id>& ids, Id id) {
    return std::find(ids.begin(), ids.end(), id) != ids.end();
}

bool valid_parameter_dimension(const ParameterVector& parameters) {
    return parameters.dimension >= 0 &&
           parameters.dimension <= static_cast<int>(parameters.values.size());
}

bool parameter_dimension_matches(const EntityDraft& entity) {
    return valid_parameter_dimension(entity.parameters) &&
           entity.parameters.dimension == geometry_dof(entity.kind);
}

void append_validation_findings(const ModelSnapshot& snapshot, StageReport& report) {
    if (snapshot.schema_version.empty()) {
        append_message(report,
                       ReportSeverity::error,
                       code("kernel.empty_schema_version"),
                       "Model schema version must be explicit.");
    }

    if (snapshot.units.length_scale <= 0.0) {
        append_message(report,
                       ReportSeverity::error,
                       code("kernel.invalid_units"),
                       "Length scale must be positive.");
    }

    if (snapshot.tolerances.residual <= 0.0 ||
        snapshot.tolerances.rank <= 0.0 ||
        snapshot.tolerances.boundary <= 0.0) {
        append_message(report,
                       ReportSeverity::error,
                       code("kernel.invalid_tolerance"),
                       "Tolerance values must be positive.");
    }

    std::vector<EntityId> entity_ids;
    for (const auto& entity : snapshot.entities) {
        if (already_seen(entity_ids, entity.id)) {
            append_message(report,
                           ReportSeverity::error,
                           code("kernel.duplicate_entity_id"),
                           "Model contains a duplicate entity ID.",
                           {subject(entity_domain, entity.id.value)});
        }
        entity_ids.push_back(entity.id);

        if (!parameter_dimension_matches(entity)) {
            append_message(report,
                           ReportSeverity::error,
                           code("kernel.invalid_parameter_dimension"),
                           "Entity parameter dimension does not match its geometry kind.",
                           {subject(entity_domain, entity.id.value)});
        }

        if (find_rigid_set(snapshot, entity.rigid_set_id) == nullptr) {
            append_message(report,
                           ReportSeverity::error,
                           code("kernel.missing_rigid_set"),
                           "Entity references a rigid set that is not present in the model.",
                           {subject(entity_domain, entity.id.value),
                            subject(rigid_set_domain, entity.rigid_set_id.value)});
        }
    }

    std::vector<ConstraintId> constraint_ids;
    for (const auto& constraint : snapshot.constraints) {
        if (already_seen(constraint_ids, constraint.id)) {
            append_message(report,
                           ReportSeverity::error,
                           code("kernel.duplicate_constraint_id"),
                           "Model contains a duplicate constraint ID.",
                           {subject(constraint_domain, constraint.id.value)});
        }
        constraint_ids.push_back(constraint.id);

        for (EntityId entity_id : constraint.entity_ids) {
            if (find_entity(snapshot, entity_id) == nullptr) {
                append_message(report,
                               ReportSeverity::error,
                               code("kernel.missing_entity"),
                               "Constraint references an entity that is not present in the model.",
                               {subject(constraint_domain, constraint.id.value),
                                subject(entity_domain, entity_id.value)});
            }
        }
    }

    std::vector<RigidSetId> rigid_set_ids;
    for (const auto& rigid_set : snapshot.rigid_sets) {
        if (already_seen(rigid_set_ids, rigid_set.id)) {
            append_message(report,
                           ReportSeverity::error,
                           code("kernel.duplicate_rigid_set_id"),
                           "Model contains a duplicate rigid set ID.",
                           {subject(rigid_set_domain, rigid_set.id.value)});
        }
        rigid_set_ids.push_back(rigid_set.id);

        for (EntityId entity_id : rigid_set.entity_ids) {
            if (find_entity(snapshot, entity_id) == nullptr) {
                append_message(report,
                               ReportSeverity::error,
                               code("kernel.missing_entity"),
                               "Rigid set references an entity that is not present in the model.",
                               {subject(rigid_set_domain, rigid_set.id.value),
                                subject(entity_domain, entity_id.value)});
            }
        }
    }
}

bool same_entity_payload(const EntityDraft& lhs, const EntityDraft& rhs) {
    return lhs.id == rhs.id &&
           lhs.kind == rhs.kind &&
           lhs.rigid_set_id == rhs.rigid_set_id &&
           lhs.parameters == rhs.parameters;
}

}

int geometry_dof(GeometryKind kind) {
    switch (kind) {
        case GeometryKind::point: return 3;
        case GeometryKind::line: return 6;
        case GeometryKind::plane: return 6;
    }
    return 0;
}

StateVersionId next_version(StateVersionId current) {
    return StateVersionId{current.value + 1};
}

ContractResult<ModelSnapshot> make_snapshot(ModelDraft draft) {
    ModelSnapshot snapshot;
    snapshot.schema_version = std::move(draft.schema_version);
    snapshot.state_version = draft.initial_state_version;
    snapshot.units = std::move(draft.units);
    snapshot.tolerances = draft.tolerances;
    snapshot.rigid_sets = std::move(draft.rigid_sets);
    snapshot.entities = std::move(draft.entities);
    snapshot.constraints = std::move(draft.constraints);

    auto validation = validate_model(snapshot);
    return ContractResult<ModelSnapshot>{std::move(snapshot), std::move(validation.report)};
}

ContractResult<ModelValidationReport> validate_model(const ModelSnapshot& snapshot) {
    ContractResult<ModelValidationReport> result;
    result.report = make_report("kernel.validate_model");
    append_validation_findings(snapshot, result.report);

    result.payload.valid = !has_errors(result.report);
    result.payload.entity_count = static_cast<int>(snapshot.entities.size());
    result.payload.constraint_count = static_cast<int>(snapshot.constraints.size());
    result.payload.rigid_set_count = static_cast<int>(snapshot.rigid_sets.size());
    return result;
}

ContractResult<ContextSnapshot> make_context(const ModelSnapshot& snapshot,
                                             ContextRequest request) {
    ContextSnapshot context;
    context.id = request.id;
    context.kind = request.kind;
    context.state_version = snapshot.state_version;

    if (request.kind == ContextKind::whole_model) {
        for (const auto& entity : snapshot.entities) {
            context.entity_ids.push_back(entity.id);
        }
        for (const auto& constraint : snapshot.constraints) {
            context.constraint_ids.push_back(constraint.id);
        }
        for (const auto& rigid_set : snapshot.rigid_sets) {
            context.rigid_set_ids.push_back(rigid_set.id);
        }
    } else {
        context.entity_ids = std::move(request.entity_ids);
        context.constraint_ids = std::move(request.constraint_ids);
        context.rigid_set_ids = std::move(request.rigid_set_ids);
    }

    auto validation = validate_context(snapshot, context);
    return ContractResult<ContextSnapshot>{std::move(context), std::move(validation.report)};
}

ContractResult<ContextValidationReport> validate_context(const ModelSnapshot& snapshot,
                                                         const ContextSnapshot& context) {
    ContractResult<ContextValidationReport> result;
    result.report = make_report("kernel.validate_context");

    for (EntityId entity_id : context.entity_ids) {
        if (find_entity(snapshot, entity_id) == nullptr) {
            append_message(result.report,
                           ReportSeverity::error,
                           code("kernel.context_missing_entity"),
                           "Context references an entity that is not present in the model.",
                           {subject(entity_domain, entity_id.value)});
        }
    }

    for (ConstraintId constraint_id : context.constraint_ids) {
        if (find_constraint(snapshot, constraint_id) == nullptr) {
            append_message(result.report,
                           ReportSeverity::error,
                           code("kernel.context_missing_constraint"),
                           "Context references a constraint that is not present in the model.",
                           {subject(constraint_domain, constraint_id.value)});
        }
    }

    for (RigidSetId rigid_set_id : context.rigid_set_ids) {
        if (find_rigid_set(snapshot, rigid_set_id) == nullptr) {
            append_message(result.report,
                           ReportSeverity::error,
                           code("kernel.context_missing_rigid_set"),
                           "Context references a rigid set that is not present in the model.",
                           {subject(rigid_set_domain, rigid_set_id.value)});
        }
    }

    if (context.kind == ContextKind::whole_model) {
        result.payload.covers_whole_model = true;
        for (const auto& entity : snapshot.entities) {
            if (!contains_entity_id(context.entity_ids, entity.id)) {
                result.payload.covers_whole_model = false;
                append_message(result.report,
                               ReportSeverity::error,
                               code("kernel.context_coverage_mismatch"),
                               "Whole-model context does not include every model entity.",
                               {subject(entity_domain, entity.id.value)});
            }
        }
        for (const auto& constraint : snapshot.constraints) {
            if (!contains_constraint_id(context.constraint_ids, constraint.id)) {
                result.payload.covers_whole_model = false;
                append_message(result.report,
                               ReportSeverity::error,
                               code("kernel.context_coverage_mismatch"),
                               "Whole-model context does not include every model constraint.",
                               {subject(constraint_domain, constraint.id.value)});
            }
        }
        for (const auto& rigid_set : snapshot.rigid_sets) {
            if (!contains_rigid_set_id(context.rigid_set_ids, rigid_set.id)) {
                result.payload.covers_whole_model = false;
                append_message(result.report,
                               ReportSeverity::error,
                               code("kernel.context_coverage_mismatch"),
                               "Whole-model context does not include every model rigid set.",
                               {subject(rigid_set_domain, rigid_set.id.value)});
            }
        }
    }

    result.payload.valid = !has_errors(result.report);
    return result;
}

ContractResult<SnapshotDiff> diff_snapshots(const ModelSnapshot& before,
                                            const ModelSnapshot& after) {
    ContractResult<SnapshotDiff> result;
    result.report = make_report("kernel.diff_snapshots");
    result.payload.same_schema = before.schema_version == after.schema_version;
    result.payload.state_version_changed = !(before.state_version == after.state_version);

    for (const auto& after_entity : after.entities) {
        const auto* before_entity = find_entity(before, after_entity.id);
        if (before_entity == nullptr) {
            result.payload.added_entities.push_back(after_entity.id);
        } else if (!same_entity_payload(*before_entity, after_entity)) {
            result.payload.changed_entities.push_back(after_entity.id);
        }
    }

    for (const auto& before_entity : before.entities) {
        if (find_entity(after, before_entity.id) == nullptr) {
            result.payload.removed_entities.push_back(before_entity.id);
        }
    }

    for (const auto& after_constraint : after.constraints) {
        if (find_constraint(before, after_constraint.id) == nullptr) {
            result.payload.added_constraints.push_back(after_constraint.id);
        }
    }

    for (const auto& before_constraint : before.constraints) {
        if (find_constraint(after, before_constraint.id) == nullptr) {
            result.payload.removed_constraints.push_back(before_constraint.id);
        }
    }

    return result;
}

ContractResult<StateDeltaValidationReport> validate_delta(const ModelSnapshot& base,
                                                          const StateDelta& delta) {
    ContractResult<StateDeltaValidationReport> result;
    result.report = make_report("kernel.validate_delta");

    result.payload.base_version_matches = delta.base_version == base.state_version;
    if (!result.payload.base_version_matches) {
        append_message(result.report,
                       ReportSeverity::error,
                       code("kernel.delta_base_version_mismatch"),
                       "State delta base version must match the model snapshot version.",
                       {subject(state_version_domain, delta.base_version.value),
                        subject(state_version_domain, base.state_version.value)});
    }

    result.payload.target_version_is_next = delta.target_version == next_version(delta.base_version);
    if (!result.payload.target_version_is_next) {
        append_message(result.report,
                       ReportSeverity::error,
                       code("kernel.delta_target_version_mismatch"),
                       "State delta target version must be the next durable state version.",
                       {subject(state_version_domain, delta.target_version.value)});
    }

    std::vector<EntityId> seen_entities;
    for (const auto& entity_state : delta.entity_states) {
        if (already_seen(seen_entities, entity_state.entity_id)) {
            append_message(result.report,
                           ReportSeverity::error,
                           code("kernel.delta_duplicate_entity_state"),
                           "State delta contains duplicate entity state.",
                           {subject(entity_domain, entity_state.entity_id.value)});
        }
        seen_entities.push_back(entity_state.entity_id);

        const auto* entity = find_entity(base, entity_state.entity_id);
        if (entity == nullptr) {
            append_message(result.report,
                           ReportSeverity::error,
                           code("kernel.delta_missing_entity"),
                           "State delta references an entity that is not present in the model.",
                           {subject(entity_domain, entity_state.entity_id.value)});
            continue;
        }

        if (!valid_parameter_dimension(entity_state.parameters) ||
            entity_state.parameters.dimension != geometry_dof(entity->kind)) {
            append_message(result.report,
                           ReportSeverity::error,
                           code("kernel.invalid_parameter_dimension"),
                           "State delta parameter dimension does not match the entity geometry.",
                           {subject(entity_domain, entity_state.entity_id.value)});
        }
    }

    result.payload.valid = !has_errors(result.report);
    return result;
}

}

namespace gcs {

bool operator==(EntityId lhs, EntityId rhs) { return lhs.value == rhs.value; }
bool operator==(ConstraintId lhs, ConstraintId rhs) { return lhs.value == rhs.value; }
bool operator==(RigidSetId lhs, RigidSetId rhs) { return lhs.value == rhs.value; }
bool operator==(ContextId lhs, ContextId rhs) { return lhs.value == rhs.value; }
bool operator==(CoverId lhs, CoverId rhs) { return lhs.value == rhs.value; }
bool operator==(ProjectionId lhs, ProjectionId rhs) { return lhs.value == rhs.value; }
bool operator==(StateVersionId lhs, StateVersionId rhs) { return lhs.value == rhs.value; }
bool operator==(ReportId lhs, ReportId rhs) { return lhs.value == rhs.value; }
bool operator==(CommandId lhs, CommandId rhs) { return lhs.value == rhs.value; }

std::string toString(GeometryKind kind) {
    switch (kind) {
        case GeometryKind::Point: return "Point";
        case GeometryKind::Line: return "Line";
        case GeometryKind::Plane: return "Plane";
    }
    return "UnknownGeometry";
}

std::string toString(ConstraintKind kind) {
    switch (kind) {
        case ConstraintKind::Coincident: return "Coincident";
        case ConstraintKind::Parallel: return "Parallel";
        case ConstraintKind::Perpendicular: return "Perpendicular";
        case ConstraintKind::Distance: return "Distance";
        case ConstraintKind::Angle: return "Angle";
    }
    return "UnknownConstraint";
}

std::string toString(SolveMode mode) {
    switch (mode) {
        case SolveMode::Update: return "Update";
        case SolveMode::Drag: return "Drag";
        case SolveMode::Simulation: return "Simulation";
    }
    return "UnknownSolveMode";
}

std::string toString(ContextKind kind) {
    switch (kind) {
        case ContextKind::WholeModel: return "WholeModel";
        case ContextKind::ConnectedComponent: return "ConnectedComponent";
        case ContextKind::RigidSet: return "RigidSet";
        case ContextKind::Subproblem: return "Subproblem";
        case ContextKind::Overlap: return "Overlap";
        case ContextKind::Gauge: return "Gauge";
    }
    return "UnknownContext";
}

std::string toString(GaugeKind kind) {
    switch (kind) {
        case GaugeKind::None: return "None";
        case GaugeKind::AnchorEntities: return "AnchorEntities";
        case GaugeKind::QuotientRigidMotion: return "QuotientRigidMotion";
    }
    return "UnknownGauge";
}

std::string toString(SolveStatus status) {
    switch (status) {
        case SolveStatus::NotRun: return "NotRun";
        case SolveStatus::Solved: return "Solved";
        case SolveStatus::AcceptedWithWarnings: return "AcceptedWithWarnings";
        case SolveStatus::InvalidModel: return "InvalidModel";
        case SolveStatus::UnderConstrained: return "UnderConstrained";
        case SolveStatus::OverConstrained: return "OverConstrained";
        case SolveStatus::Redundant: return "Redundant";
        case SolveStatus::Inconsistent: return "Inconsistent";
        case SolveStatus::NumericallySingular: return "NumericallySingular";
        case SolveStatus::Unsupported: return "Unsupported";
        case SolveStatus::Failed: return "Failed";
    }
    return "UnknownSolveStatus";
}

std::string toString(StageStatus status) {
    switch (status) {
        case StageStatus::Ok: return "Ok";
        case StageStatus::Warning: return "Warning";
        case StageStatus::Error: return "Error";
        case StageStatus::Unsupported: return "Unsupported";
    }
    return "UnknownStageStatus";
}

int geometryDof(GeometryKind kind) {
    switch (kind) {
        case GeometryKind::Point: return 3;
        case GeometryKind::Line: return 6;
        case GeometryKind::Plane: return 6;
    }
    return 0;
}

int constraintDofEffect(ConstraintKind kind) {
    switch (kind) {
        case ConstraintKind::Coincident: return 3;
        case ConstraintKind::Parallel: return 2;
        case ConstraintKind::Perpendicular: return 1;
        case ConstraintKind::Distance: return 1;
        case ConstraintKind::Angle: return 1;
    }
    return 0;
}

const GeometricEntity* findEntity(const ModelSnapshot& model, EntityId id) {
    for (const auto& entity : model.entities) {
        if (entity.id == id) return &entity;
    }
    return nullptr;
}

const ConstraintInstance* findConstraint(const ModelSnapshot& model, ConstraintId id) {
    for (const auto& constraint : model.constraints) {
        if (constraint.id == id) return &constraint;
    }
    return nullptr;
}

const RigidSet* findRigidSet(const ModelSnapshot& model, RigidSetId id) {
    for (const auto& rigidSet : model.rigidSets) {
        if (rigidSet.id == id) return &rigidSet;
    }
    return nullptr;
}

bool containsEntity(const std::vector<EntityId>& ids, EntityId id) {
    return std::find(ids.begin(), ids.end(), id) != ids.end();
}

bool containsConstraint(const std::vector<ConstraintId>& ids, ConstraintId id) {
    return std::find(ids.begin(), ids.end(), id) != ids.end();
}

bool containsRigidSet(const std::vector<RigidSetId>& ids, RigidSetId id) {
    return std::find(ids.begin(), ids.end(), id) != ids.end();
}

ContextSnapshot makeWholeModelContext(const ModelSnapshot& model, ContextId id) {
    ContextSnapshot context;
    context.id = id;
    context.kind = ContextKind::WholeModel;
    for (const auto& entity : model.entities) {
        context.entityIds.push_back(entity.id);
    }
    for (const auto& constraint : model.constraints) {
        context.constraintIds.push_back(constraint.id);
    }
    for (const auto& rigidSet : model.rigidSets) {
        context.rigidSetIds.push_back(rigidSet.id);
    }
    return context;
}

std::vector<EntityState> captureEntityStates(const ModelSnapshot& model,
                                             const std::vector<EntityId>& entityIds) {
    std::vector<EntityState> states;
    for (EntityId id : entityIds) {
        if (const auto* entity = findEntity(model, id)) {
            states.push_back(EntityState{entity->id, entity->parameters});
        }
    }
    return states;
}

StateVersionId nextVersion(StateVersionId current) {
    return StateVersionId{current.value + 1};
}

StageReport makeStageReport(std::string stage, StageStatus status) {
    StageReport report;
    report.stage = std::move(stage);
    report.status = status;
    return report;
}

}
