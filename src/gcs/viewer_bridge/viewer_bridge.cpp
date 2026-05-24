module;

#include <string>
#include <utility>
#include <vector>

module gcs.viewer_bridge;

import gcs.kernel;
import gcs.session_runtime;

namespace gcs::viewer {

namespace kernel = gcs::kernel;

namespace {

bool viewer_contains_entity(const std::vector<EntityId>& ids, EntityId id) {
    for (EntityId candidate : ids) {
        if (candidate == id) return true;
    }
    return false;
}

bool viewer_contains_constraint(const std::vector<ConstraintId>& ids, ConstraintId id) {
    for (ConstraintId candidate : ids) {
        if (candidate == id) return true;
    }
    return false;
}

SolveStatus status_from_stage(kernel::StageStatus status) {
    switch (status) {
        case kernel::StageStatus::ok: return SolveStatus::solved;
        case kernel::StageStatus::warning: return SolveStatus::accepted_with_warnings;
        case kernel::StageStatus::error: return SolveStatus::failed;
        case kernel::StageStatus::unsupported: return SolveStatus::unsupported;
    }
    return SolveStatus::not_run;
}

OverlayItem make_overlay_item(const kernel::ReportMessage& message,
                              SolveStatus status) {
    OverlayItem item;
    item.code = message.code.value;
    item.message = message.summary;
    item.status = status;
    for (const auto& subject : message.subjects) {
        if (subject.domain == "entity") {
            item.entity_ids.push_back(EntityId{subject.value});
        } else if (subject.domain == "constraint") {
            item.constraint_ids.push_back(ConstraintId{subject.value});
        }
    }
    return item;
}

std::string rank_evidence_message(
    const runtime::RankEvidenceProjection& evidence) {
    return "rank " + std::to_string(evidence.numeric_rank_estimate) +
           ", variables " +
           std::to_string(evidence.numeric_variable_dimension) +
           ", free " +
           std::to_string(evidence.numeric_free_variable_dimension) +
           ", frozen " +
           std::to_string(evidence.numeric_frozen_variable_dimension) +
           ", residuals " +
           std::to_string(evidence.numeric_residual_dimension) +
           ", nullity " +
           std::to_string(evidence.numeric_nullity_estimate);
}

}  // namespace

gcs::kernel::ContractResult<ViewerSceneProjection> project_scene(
    ViewerProjectionRequest request) {
    kernel::ContractResult<ViewerSceneProjection> result;
    result.report = kernel::make_stage_report("viewer_bridge.project_scene");

    result.payload.schema_version = request.snapshot.schema_version;
    result.payload.state_version = request.snapshot.state_version;
    result.payload.rigid_set_count = static_cast<int>(request.snapshot.rigid_sets.size());

    for (const auto& entity : request.snapshot.entities) {
        ProjectedEntity projected;
        projected.id = entity.id;
        projected.kind = entity.kind;
        projected.rigid_set_id = entity.rigid_set_id;
        projected.parameters.assign(
            entity.parameters.values.begin(),
            entity.parameters.values.end());
        projected.selected = viewer_contains_entity(request.selected_entities, entity.id);
        result.payload.entities.push_back(std::move(projected));
    }

    for (const auto& constraint : request.snapshot.constraints) {
        ProjectedConstraint projected;
        projected.id = constraint.id;
        projected.kind = constraint.kind;
        projected.entity_ids = constraint.entity_ids;
        projected.value = constraint.value;
        projected.selected =
            viewer_contains_constraint(request.selected_constraints, constraint.id);
        result.payload.constraints.push_back(std::move(projected));
    }

    return result;
}

gcs::kernel::ContractResult<DiagnosticOverlay> build_overlay(
    DiagnosticOverlayRequest request) {
    kernel::ContractResult<DiagnosticOverlay> result;
    result.report = kernel::make_stage_report("viewer_bridge.build_overlay");

    result.payload.status = request.command_result.user_visible_status;
    result.payload.accepted = request.command_result.accepted;
    result.payload.state_version = request.snapshot.state_version;
    result.payload.rank_evidence =
        runtime::project_rank_evidence(request.command_result);

    OverlayItem status_item;
    status_item.code = "viewer.status";
    status_item.message = kernel::to_string(request.command_result.user_visible_status);
    status_item.status = request.command_result.user_visible_status;
    result.payload.items.push_back(std::move(status_item));

    for (const auto& report : request.command_result.stage_reports) {
        if (request.verbosity == DiagnosticVerbosity::detailed) {
            OverlayItem stage_item;
            stage_item.code = report.stage;
            stage_item.message = kernel::to_string(report.status);
            stage_item.status = status_from_stage(report.status);
            result.payload.items.push_back(std::move(stage_item));
        }
        for (const auto& message : report.messages) {
            result.payload.items.push_back(make_overlay_item(
                message,
                request.command_result.user_visible_status));
        }
    }

    if (request.verbosity == DiagnosticVerbosity::detailed) {
        for (const auto& evidence : result.payload.rank_evidence) {
            OverlayItem rank_item;
            rank_item.code = "viewer.rank_evidence";
            rank_item.message = rank_evidence_message(evidence);
            rank_item.status = evidence.result_status;
            result.payload.items.push_back(std::move(rank_item));
        }
    }

    if (request.command_result.obstruction_report.present) {
        OverlayItem obstruction;
        obstruction.code = request.command_result.obstruction_report.code;
        obstruction.message = request.command_result.obstruction_report.message;
        obstruction.status = request.command_result.user_visible_status;
        obstruction.entity_ids = request.command_result.obstruction_report.entity_ids;
        obstruction.constraint_ids =
            request.command_result.obstruction_report.constraint_ids;
        result.payload.items.push_back(std::move(obstruction));
    }

    return result;
}

gcs::kernel::ContractResult<InteractionCommandDraft> draft_command(
    InteractionDraftRequest request) {
    kernel::ContractResult<InteractionCommandDraft> result;
    result.report = kernel::make_stage_report("viewer_bridge.draft_command");

    result.payload.command.id = request.command_id;
    result.payload.command.kind = runtime::CommandKind::solve;
    result.payload.command.solve_intent = request.solve_intent;
    result.payload.command.model_edit_or_solve_request = request.snapshot;

    auto validation = runtime::validate_command(request.snapshot, result.payload.command);
    result.payload.valid = validation.payload.valid;
    result.payload.messages = validation.payload.messages;
    for (auto message : validation.report.messages) {
        kernel::append_report_message(result.report, std::move(message));
    }
    return result;
}

gcs::kernel::ContractResult<HistoryFrameProjection> project_history_frame(
    HistoryFrameRequest request) {
    kernel::ContractResult<HistoryFrameProjection> result;
    result.report = kernel::make_stage_report("viewer_bridge.project_history_frame");

    result.payload.valid = request.frame_index >= 0 &&
                           request.frame_index <
                               static_cast<int>(request.event.transaction_trace.stages.size());
    result.payload.command_id = request.event.command_id;
    result.payload.base_version = request.event.base_version;
    result.payload.new_state_version = request.event.new_state_version;
    result.payload.status = request.event.status;
    result.payload.stages = request.event.transaction_trace.stages;

    if (!result.payload.valid) {
        kernel::append_report_message(
            result.report,
            kernel::make_report_message(
                kernel::ReportSeverity::error,
                kernel::ReportCode{"viewer.history_frame_out_of_range"},
                "Requested history frame is outside the transaction trace."));
    }

    return result;
}

SnapshotSummary summarize_snapshot(const ModelSnapshot& snapshot) {
    SnapshotSummary summary;
    summary.rigid_set_count = static_cast<int>(snapshot.rigid_sets.size());
    summary.entity_count = static_cast<int>(snapshot.entities.size());
    summary.constraint_count = static_cast<int>(snapshot.constraints.size());
    summary.state_version = snapshot.state_version.value;
    return summary;
}

SnapshotSummary summarize_command_result(const ModelSnapshot& snapshot,
                                         const runtime::CommandResult& result) {
    SnapshotSummary summary = summarize_snapshot(snapshot);
    summary.last_status = result.user_visible_status;
    summary.rank_evidence = runtime::project_rank_evidence(result);
    for (const auto& evidence : summary.rank_evidence) {
        summary.messages.push_back(
            evidence.source + ": " + rank_evidence_message(evidence));
    }
    for (const auto& report : result.stage_reports) {
        summary.messages.push_back(report.stage + ": " + kernel::to_string(report.status));
        for (const auto& message : report.messages) {
            summary.messages.push_back(message.code.value + ": " + message.summary);
        }
    }
    if (result.obstruction_report.present) {
        summary.messages.push_back(result.obstruction_report.code + ": " +
                                   result.obstruction_report.message);
    }
    return summary;
}

std::string solve_status_text(SolveStatus status) {
    return kernel::to_string(status);
}

}
