module;

#include <cstdint>
#include <string>
#include <vector>

export module gcs.viewer_bridge;

export import gcs.kernel;
export import gcs.session_runtime;

export namespace gcs::viewer {

using gcs::kernel::CommandId;
using gcs::kernel::ConstraintId;
using gcs::kernel::ConstraintKind;
using gcs::kernel::EntityId;
using gcs::kernel::GeometryKind;
using gcs::kernel::ModelSnapshot;
using gcs::kernel::ReportMessage;
using gcs::kernel::RigidSetId;
using gcs::kernel::SolveStatus;
using gcs::kernel::StateVersionId;

enum class ProjectionMode {
    compact,
    detailed,
};

enum class DiagnosticVerbosity {
    summary,
    detailed,
};

enum class InteractionKind {
    solve,
};

struct ProjectedEntity {
    EntityId id;
    GeometryKind kind = GeometryKind::point;
    RigidSetId rigid_set_id;
    std::vector<double> parameters;
    bool selected = false;
};

struct ProjectedConstraint {
    ConstraintId id;
    ConstraintKind kind = ConstraintKind::coincident;
    std::vector<EntityId> entity_ids;
    double value = 0.0;
    bool selected = false;
};

struct ViewerProjectionRequest {
    ModelSnapshot snapshot;
    std::vector<EntityId> selected_entities;
    std::vector<ConstraintId> selected_constraints;
    ProjectionMode mode = ProjectionMode::compact;
};

struct ViewerSceneProjection {
    std::string schema_version;
    StateVersionId state_version;
    int rigid_set_count = 0;
    std::vector<ProjectedEntity> entities;
    std::vector<ProjectedConstraint> constraints;
};

struct DiagnosticOverlayRequest {
    ModelSnapshot snapshot;
    runtime::CommandResult command_result;
    DiagnosticVerbosity verbosity = DiagnosticVerbosity::summary;
};

struct OverlayItem {
    std::string code;
    std::string message;
    SolveStatus status = SolveStatus::not_run;
    std::vector<EntityId> entity_ids;
    std::vector<ConstraintId> constraint_ids;
};

struct DiagnosticOverlay {
    SolveStatus status = SolveStatus::not_run;
    bool accepted = false;
    StateVersionId state_version;
    std::vector<runtime::RankEvidenceProjection> rank_evidence;
    std::vector<OverlayItem> items;
};

struct InteractionDraftRequest {
    ModelSnapshot snapshot;
    InteractionKind kind = InteractionKind::solve;
    CommandId command_id{1};
    gcs::kernel::SolveIntent solve_intent;
};

struct InteractionCommandDraft {
    bool valid = false;
    runtime::Command command;
    std::vector<ReportMessage> messages;
};

struct HistoryFrameRequest {
    runtime::HistoryEvent event;
    int frame_index = 0;
};

struct HistoryFrameProjection {
    bool valid = false;
    CommandId command_id;
    StateVersionId base_version;
    StateVersionId new_state_version;
    SolveStatus status = SolveStatus::not_run;
    std::vector<runtime::StageTraceEntry> stages;
};

struct SnapshotSummary {
    int rigid_set_count = 0;
    int entity_count = 0;
    int constraint_count = 0;
    std::uint64_t state_version = 0;
    SolveStatus last_status = SolveStatus::not_run;
    std::vector<runtime::RankEvidenceProjection> rank_evidence;
    std::vector<std::string> messages;
};

gcs::kernel::ContractResult<ViewerSceneProjection> project_scene(
    ViewerProjectionRequest request);
gcs::kernel::ContractResult<DiagnosticOverlay> build_overlay(
    DiagnosticOverlayRequest request);
gcs::kernel::ContractResult<InteractionCommandDraft> draft_command(
    InteractionDraftRequest request);
gcs::kernel::ContractResult<HistoryFrameProjection> project_history_frame(
    HistoryFrameRequest request);
SnapshotSummary summarize_snapshot(const ModelSnapshot& snapshot);
SnapshotSummary summarize_command_result(const ModelSnapshot& snapshot,
                                         const runtime::CommandResult& result);
std::string solve_status_text(SolveStatus status);

}
