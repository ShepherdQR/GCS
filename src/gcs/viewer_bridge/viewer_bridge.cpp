module;

#include <cstddef>
#include <iomanip>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

module gcs.viewer_bridge;

import gcs.kernel;
import gcs.session_runtime;

namespace gcs::viewer {

namespace kernel = gcs::kernel;
namespace diagnostics = gcs::diagnostics;

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

std::string residual_evidence_message(
    const ResidualEvidenceProjection& evidence) {
    return "residuals " + std::to_string(evidence.residual_dimension) +
           ", norm " + std::to_string(evidence.total_residual) +
           ", max " + std::to_string(evidence.max_residual);
}

std::string bool_text(bool value) {
    return value ? "true" : "false";
}

std::string replay_artifact_kind_text(runtime::ReplayArtifactKind kind) {
    switch (kind) {
        case runtime::ReplayArtifactKind::runtime_transaction_trace:
            return "runtime_transaction_trace";
    }
    return "unknown";
}

std::string stage_summary_line(
    const runtime::RuntimeReplayEvidenceStage& stage) {
    return "[" + std::to_string(stage.order) + "] " + stage.stage +
           " stage_status=" + kernel::to_string(stage.stage_status) +
           " status=" + kernel::to_string(stage.status) +
           " versions=" + std::to_string(stage.before_version.value) + "->" +
           std::to_string(stage.after_version.value) +
           " durable=" + bool_text(stage.durable_mutation) +
           " code=" + stage.report_code;
}

std::string json_string(const std::string& value) {
    std::string output = "\"";
    for (unsigned char ch : value) {
        switch (ch) {
            case '"': output += "\\\""; break;
            case '\\': output += "\\\\"; break;
            case '\b': output += "\\b"; break;
            case '\f': output += "\\f"; break;
            case '\n': output += "\\n"; break;
            case '\r': output += "\\r"; break;
            case '\t': output += "\\t"; break;
            default:
                if (ch < 0x20) {
                    std::ostringstream escape;
                    escape << "\\u" << std::hex << std::setw(4)
                           << std::setfill('0') << static_cast<int>(ch);
                    output += escape.str();
                } else {
                    output.push_back(static_cast<char>(ch));
                }
                break;
        }
    }
    output += "\"";
    return output;
}

ResponsibilityEvidenceProjection make_conflict_projection(
    std::string source,
    const diagnostics::ConflictSet& conflict) {
    ResponsibilityEvidenceProjection projection;
    projection.source = std::move(source);
    projection.code = conflict.code;
    projection.entity_ids = conflict.entity_ids;
    projection.constraint_ids = conflict.constraint_ids;
    return projection;
}

ResponsibilityEvidenceProjection make_redundancy_projection(
    std::string source,
    const diagnostics::RedundancySet& redundancy) {
    ResponsibilityEvidenceProjection projection;
    projection.source = std::move(source);
    projection.code = redundancy.code;
    projection.constraint_ids = redundancy.constraint_ids;
    return projection;
}

ResponsibilityEvidenceProjection make_obstruction_projection(
    std::string source,
    const diagnostics::ObstructionReport& obstruction) {
    ResponsibilityEvidenceProjection projection;
    projection.source = std::move(source);
    projection.code = obstruction.code;
    projection.entity_ids = obstruction.entity_ids;
    projection.constraint_ids = obstruction.constraint_ids;
    return projection;
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
    result.payload.residual_evidence =
        project_residual_evidence(request.command_result);
    result.payload.conflict_evidence =
        project_conflict_evidence(request.command_result);
    result.payload.redundancy_evidence =
        project_redundancy_evidence(request.command_result);
    result.payload.obstruction_evidence =
        project_obstruction_evidence(request.command_result);

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
        for (const auto& evidence : result.payload.residual_evidence) {
            OverlayItem residual_item;
            residual_item.code = "viewer.residual_evidence";
            residual_item.message = residual_evidence_message(evidence);
            residual_item.status = request.command_result.user_visible_status;
            result.payload.items.push_back(std::move(residual_item));
        }
        for (const auto& evidence : result.payload.conflict_evidence) {
            OverlayItem conflict_item;
            conflict_item.code = "viewer.conflict_evidence";
            conflict_item.message = evidence.code;
            conflict_item.status = request.command_result.user_visible_status;
            conflict_item.entity_ids = evidence.entity_ids;
            conflict_item.constraint_ids = evidence.constraint_ids;
            result.payload.items.push_back(std::move(conflict_item));
        }
        for (const auto& evidence : result.payload.redundancy_evidence) {
            OverlayItem redundancy_item;
            redundancy_item.code = "viewer.redundancy_evidence";
            redundancy_item.message = evidence.code;
            redundancy_item.status = request.command_result.user_visible_status;
            redundancy_item.entity_ids = evidence.entity_ids;
            redundancy_item.constraint_ids = evidence.constraint_ids;
            result.payload.items.push_back(std::move(redundancy_item));
        }
        for (const auto& evidence : result.payload.obstruction_evidence) {
            OverlayItem obstruction_item;
            obstruction_item.code = "viewer.obstruction_evidence";
            obstruction_item.message = evidence.code;
            obstruction_item.status = request.command_result.user_visible_status;
            obstruction_item.entity_ids = evidence.entity_ids;
            obstruction_item.constraint_ids = evidence.constraint_ids;
            result.payload.items.push_back(std::move(obstruction_item));
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
    result.payload.replay_artifact_kind = request.event.replay_artifact_kind;
    result.payload.scene_construction_history_entry =
        request.event.scene_construction_history_entry;
    result.payload.report_evidence = request.event.report_evidence;
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

gcs::kernel::ContractResult<ReplayEvidenceSummary> summarize_replay_evidence(
    const runtime::RuntimeReplayEvidenceExport& evidence) {
    kernel::ContractResult<ReplayEvidenceSummary> result;
    result.report = kernel::make_stage_report(
        "viewer_bridge.summarize_replay_evidence");

    result.payload.found = evidence.found;
    result.payload.replay_artifact_kind = evidence.replay_artifact_kind;
    result.payload.replay_artifact_kind_text =
        replay_artifact_kind_text(evidence.replay_artifact_kind);
    result.payload.scene_construction_history_entry =
        evidence.scene_construction_history_entry;
    result.payload.report_evidence = evidence.report_evidence;
    result.payload.command_id = evidence.command_id;
    result.payload.accepted = evidence.accepted;
    result.payload.status = kernel::to_string(evidence.status);
    result.payload.base_version = evidence.base_version;
    result.payload.final_version = evidence.final_version;
    result.payload.committed = evidence.committed;
    result.payload.rolled_back = evidence.rolled_back;
    result.payload.report_codes = evidence.report_codes;

    if (!evidence.found) {
        kernel::append_report_message(
            result.report,
            kernel::make_report_message(
                kernel::ReportSeverity::warning,
                kernel::ReportCode{"viewer.replay_evidence_missing_command"},
                "Requested runtime replay evidence was not found."));
    }

    for (const auto& stage : evidence.stages) {
        ReplayEvidenceStageSummary summary;
        summary.order = stage.order;
        summary.stage = stage.stage;
        summary.stage_status = kernel::to_string(stage.stage_status);
        summary.status = kernel::to_string(stage.status);
        summary.before_version = stage.before_version;
        summary.after_version = stage.after_version;
        summary.durable_mutation = stage.durable_mutation;
        summary.report_code = stage.report_code;
        summary.line = stage_summary_line(stage);
        result.payload.stages.push_back(std::move(summary));
    }

    return result;
}

std::string format_replay_evidence_summary(
    const ReplayEvidenceSummary& summary) {
    std::string text;
    text += "Runtime replay evidence\n";
    text += "  found: " + bool_text(summary.found) + "\n";
    text += "  command_id: " + std::to_string(summary.command_id.value) + "\n";
    text += "  artifact: " + summary.replay_artifact_kind_text + "\n";
    text += "  report_evidence: " + bool_text(summary.report_evidence) + "\n";
    text += "  scene_history: " +
            bool_text(summary.scene_construction_history_entry) + "\n";
    text += "  accepted: " + bool_text(summary.accepted) + "\n";
    text += "  status: " + summary.status + "\n";
    text += "  versions: " + std::to_string(summary.base_version.value) +
            " -> " + std::to_string(summary.final_version.value) + "\n";
    text += "  committed: " + bool_text(summary.committed) + "\n";
    text += "  rolled_back: " + bool_text(summary.rolled_back) + "\n";
    text += "  report_codes:\n";
    if (summary.report_codes.empty()) {
        text += "    <none>\n";
    } else {
        for (const auto& code : summary.report_codes) {
            text += "    " + code + "\n";
        }
    }
    text += "  stages:\n";
    if (summary.stages.empty()) {
        text += "    <none>\n";
    } else {
        for (const auto& stage : summary.stages) {
            text += "    " + stage.line + "\n";
        }
    }
    return text;
}

gcs::kernel::ContractResult<ReplayEvidenceReportArtifact>
build_replay_evidence_report_artifact(
    const runtime::RuntimeReplayEvidenceExport& evidence) {
    kernel::ContractResult<ReplayEvidenceReportArtifact> result;
    result.report = kernel::make_stage_report(
        "viewer_bridge.build_replay_evidence_report_artifact");

    auto summary = summarize_replay_evidence(evidence);
    result.payload.summary = std::move(summary.payload);
    for (auto message : summary.report.messages) {
        kernel::append_report_message(result.report, std::move(message));
    }
    return result;
}

std::string format_replay_evidence_report_json(
    const ReplayEvidenceReportArtifact& artifact) {
    const auto& summary = artifact.summary;
    std::ostringstream output;
    output << "{\n";
    output << "  \"schema\": " << json_string(artifact.schema_version) << ",\n";
    output << "  \"content_type\": " << json_string(artifact.content_type) << ",\n";
    output << "  \"found\": " << bool_text(summary.found) << ",\n";
    output << "  \"command_id\": " << summary.command_id.value << ",\n";
    output << "  \"artifact_kind\": "
           << json_string(summary.replay_artifact_kind_text) << ",\n";
    output << "  \"report_evidence\": " << bool_text(summary.report_evidence)
           << ",\n";
    output << "  \"scene_construction_history_entry\": "
           << bool_text(summary.scene_construction_history_entry) << ",\n";
    output << "  \"accepted\": " << bool_text(summary.accepted) << ",\n";
    output << "  \"status\": " << json_string(summary.status) << ",\n";
    output << "  \"base_version\": " << summary.base_version.value << ",\n";
    output << "  \"final_version\": " << summary.final_version.value << ",\n";
    output << "  \"committed\": " << bool_text(summary.committed) << ",\n";
    output << "  \"rolled_back\": " << bool_text(summary.rolled_back) << ",\n";
    output << "  \"report_codes\": [";
    for (std::size_t index = 0; index < summary.report_codes.size(); ++index) {
        if (index > 0) output << ", ";
        output << json_string(summary.report_codes[index]);
    }
    output << "],\n";
    output << "  \"stages\": [\n";
    for (std::size_t index = 0; index < summary.stages.size(); ++index) {
        const auto& stage = summary.stages[index];
        output << "    {\"order\": " << stage.order
               << ", \"stage\": " << json_string(stage.stage)
               << ", \"stage_status\": " << json_string(stage.stage_status)
               << ", \"status\": " << json_string(stage.status)
               << ", \"before_version\": " << stage.before_version.value
               << ", \"after_version\": " << stage.after_version.value
               << ", \"durable_mutation\": "
               << bool_text(stage.durable_mutation)
               << ", \"report_code\": " << json_string(stage.report_code)
               << "}";
        if (index + 1 < summary.stages.size()) output << ",";
        output << "\n";
    }
    output << "  ]\n";
    output << "}\n";
    return output.str();
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
    summary.residual_evidence = project_residual_evidence(result);
    summary.conflict_evidence = project_conflict_evidence(result);
    summary.redundancy_evidence = project_redundancy_evidence(result);
    summary.obstruction_evidence = project_obstruction_evidence(result);
    for (const auto& evidence : summary.rank_evidence) {
        summary.messages.push_back(
            evidence.source + ": " + rank_evidence_message(evidence));
    }
    for (const auto& evidence : summary.residual_evidence) {
        summary.messages.push_back(
            evidence.source + ": " + residual_evidence_message(evidence));
    }
    for (const auto& evidence : summary.conflict_evidence) {
        summary.messages.push_back(evidence.source + ": " + evidence.code);
    }
    for (const auto& evidence : summary.redundancy_evidence) {
        summary.messages.push_back(evidence.source + ": " + evidence.code);
    }
    for (const auto& evidence : summary.obstruction_evidence) {
        summary.messages.push_back(evidence.source + ": " + evidence.code);
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

std::vector<ResidualEvidenceProjection> project_residual_evidence(
    const runtime::CommandResult& result) {
    std::vector<ResidualEvidenceProjection> projections;
    for (const auto& post_local : result.post_local_diagnostics) {
        const auto& report = post_local.diagnostic_output.residual_report;
        if (!report.from_numeric_report && report.constraints.empty()) {
            continue;
        }

        ResidualEvidenceProjection projection;
        projection.local_report_index = post_local.local_report_index;
        projection.source = "runtime.post_local_diagnostics.residual_report";
        projection.context_id = post_local.context_id;
        projection.residual_dimension = report.residual_dimension;
        projection.total_residual = report.total_residual;
        projection.max_residual = report.max_residual;
        projection.within_tolerance = report.within_tolerance;
        for (const auto& residual : report.constraints) {
            projection.constraints.push_back(
                ConstraintResidualProjection{
                    residual.constraint_id,
                    residual.dimension,
                    residual.residual,
                    residual.max_abs_value,
                    residual.tolerance,
                    residual.satisfied});
        }
        projections.push_back(std::move(projection));
    }
    return projections;
}

std::vector<ResponsibilityEvidenceProjection> project_conflict_evidence(
    const runtime::CommandResult& result) {
    std::vector<ResponsibilityEvidenceProjection> projections;
    for (const auto& conflict : result.pre_solve_diagnostics.conflict_sets) {
        projections.push_back(make_conflict_projection(
            "runtime.pre_solve_diagnostics.conflict_sets",
            conflict));
    }
    for (const auto& post_local : result.post_local_diagnostics) {
        for (const auto& conflict : post_local.diagnostic_output.conflict_sets) {
            projections.push_back(make_conflict_projection(
                "runtime.post_local_diagnostics.conflict_sets",
                conflict));
        }
    }
    for (const auto& conflict : result.gluing_report.conflict_sets) {
        projections.push_back(make_conflict_projection(
            "runtime.gluing.conflict_sets",
            conflict));
    }
    return projections;
}

std::vector<ResponsibilityEvidenceProjection> project_redundancy_evidence(
    const runtime::CommandResult& result) {
    std::vector<ResponsibilityEvidenceProjection> projections;
    for (const auto& redundancy : result.pre_solve_diagnostics.redundancy_sets) {
        projections.push_back(make_redundancy_projection(
            "runtime.pre_solve_diagnostics.redundancy_sets",
            redundancy));
    }
    for (const auto& post_local : result.post_local_diagnostics) {
        for (const auto& redundancy : post_local.diagnostic_output.redundancy_sets) {
            projections.push_back(make_redundancy_projection(
                "runtime.post_local_diagnostics.redundancy_sets",
                redundancy));
        }
    }
    for (const auto& redundancy : result.gluing_report.redundancy_sets) {
        projections.push_back(make_redundancy_projection(
            "runtime.gluing.redundancy_sets",
            redundancy));
    }
    return projections;
}

std::vector<ResponsibilityEvidenceProjection> project_obstruction_evidence(
    const runtime::CommandResult& result) {
    std::vector<ResponsibilityEvidenceProjection> projections;
    if (result.obstruction_report.present) {
        projections.push_back(make_obstruction_projection(
            "runtime.obstruction_report",
            result.obstruction_report));
    }
    if (result.gluing_report.obstruction_report.present) {
        projections.push_back(make_obstruction_projection(
            "runtime.gluing.obstruction_report",
            result.gluing_report.obstruction_report));
    }
    return projections;
}

std::string solve_status_text(SolveStatus status) {
    return kernel::to_string(status);
}

}
