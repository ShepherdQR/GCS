module;

#include <algorithm>
#include <string>
#include <utility>
#include <vector>

module gcs.kernel;

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
