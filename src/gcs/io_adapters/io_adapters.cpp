module;

#include <cstdint>
#include <cstddef>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

module gcs.io_adapters;

import gcs.kernel;

namespace gcs::io {

namespace kernel = gcs::kernel;

namespace {

bool has_json_extension(const std::string& path) {
    return path.size() >= 5 && path.substr(path.size() - 5) == ".json";
}

SceneFormat detect_format(const SceneLoadRequest& request) {
    if (!request.auto_detect_format) return request.format;
    return has_json_extension(request.path) ? SceneFormat::json : SceneFormat::text;
}

ParseIssue make_issue(ReportSeverity severity,
                      std::string code,
                      std::string message,
                      int line = 0,
                      int column = 0) {
    ParseIssue issue;
    issue.severity = severity;
    issue.code = std::move(code);
    issue.message = std::move(message);
    issue.line = line;
    issue.column = column;
    return issue;
}

void append_issue(SceneLoadResult& result, ParseIssue issue) {
    result.errors.push_back(issue.code + ": " + issue.message);
    result.parse_issues.push_back(issue);
    result.validation_report.issues.push_back(std::move(issue));
}

void append_issue(SceneWriteResult& result, ParseIssue issue) {
    result.errors.push_back(issue.code + ": " + issue.message);
    result.issues.push_back(std::move(issue));
}

kernel::EntityDraft* find_entity(ModelSnapshot& snapshot, kernel::EntityId id) {
    for (auto& entity : snapshot.entities) {
        if (entity.id == id) return &entity;
    }
    return nullptr;
}

kernel::ConstraintDraft* find_constraint(ModelSnapshot& snapshot, kernel::ConstraintId id) {
    for (auto& constraint : snapshot.constraints) {
        if (constraint.id == id) return &constraint;
    }
    return nullptr;
}

bool parse_text_scene(std::istream& input, SceneLoadResult& result) {
    int rigid_set_count = 0;
    if (!(input >> rigid_set_count)) {
        append_issue(
            result,
            make_issue(
                ReportSeverity::error,
                "io.parse.rigid_set_count",
                "Failed to read rigid set count."));
        return false;
    }

    for (int i = 0; i < rigid_set_count; ++i) {
        std::uint64_t id = 0;
        if (!(input >> id)) {
            append_issue(
                result,
                make_issue(
                    ReportSeverity::error,
                    "io.parse.rigid_set_id",
                    "Failed to read rigid set ID."));
            return false;
        }
        result.snapshot.rigid_sets.push_back(
            kernel::RigidSetDraft{kernel::RigidSetId{id}, {}});
    }

    int entity_count = 0;
    if (!(input >> entity_count)) {
        append_issue(
            result,
            make_issue(
                ReportSeverity::error,
                "io.parse.entity_count",
                "Failed to read entity count."));
        return false;
    }

    for (int i = 0; i < entity_count; ++i) {
        std::uint64_t id = 0;
        int kind = 0;
        std::uint64_t rigid_set_id = 0;
        if (!(input >> id >> kind >> rigid_set_id)) {
            append_issue(
                result,
                make_issue(
                    ReportSeverity::error,
                    "io.parse.entity_header",
                    "Failed to read entity header."));
            return false;
        }

        kernel::EntityDraft entity;
        entity.id = kernel::EntityId{id};
        entity.kind = static_cast<kernel::GeometryKind>(kind);
        entity.rigid_set_id = kernel::RigidSetId{rigid_set_id};
        entity.parameters.dimension = kernel::geometry_dof(entity.kind);
        result.snapshot.entities.push_back(entity);

        for (auto& rigid_set : result.snapshot.rigid_sets) {
            if (rigid_set.id == entity.rigid_set_id) {
                rigid_set.entity_ids.push_back(entity.id);
                break;
            }
        }
    }

    int constraint_count = 0;
    if (!(input >> constraint_count)) {
        append_issue(
            result,
            make_issue(
                ReportSeverity::error,
                "io.parse.constraint_count",
                "Failed to read constraint count."));
        return false;
    }

    for (int i = 0; i < constraint_count; ++i) {
        std::uint64_t id = 0;
        int kind = 0;
        int arity = 0;
        if (!(input >> id >> kind >> arity)) {
            append_issue(
                result,
                make_issue(
                    ReportSeverity::error,
                    "io.parse.constraint_header",
                    "Failed to read constraint header."));
            return false;
        }

        kernel::ConstraintDraft constraint;
        constraint.id = kernel::ConstraintId{id};
        constraint.kind = static_cast<kernel::ConstraintKind>(kind);
        for (int j = 0; j < arity; ++j) {
            std::uint64_t entity_id = 0;
            if (!(input >> entity_id)) {
                append_issue(
                    result,
                    make_issue(
                        ReportSeverity::error,
                        "io.parse.constraint_entity",
                        "Failed to read constraint entity reference."));
                return false;
            }
            constraint.entity_ids.push_back(kernel::EntityId{entity_id});
        }
        result.snapshot.constraints.push_back(constraint);
    }

    for (int i = 0; i < entity_count; ++i) {
        std::uint64_t id = 0;
        if (!(input >> id)) {
            append_issue(
                result,
                make_issue(
                    ReportSeverity::error,
                    "io.parse.entity_parameters",
                    "Failed to read entity parameter block."));
            return false;
        }
        auto* entity = find_entity(result.snapshot, kernel::EntityId{id});
        if (entity == nullptr) {
            append_issue(
                result,
                make_issue(
                    ReportSeverity::error,
                    "io.parse.entity_parameters_missing_entity",
                    "Entity parameter block references a missing entity."));
            return false;
        }
        for (double& value : entity->parameters.values) {
            if (!(input >> value)) {
                append_issue(
                    result,
                    make_issue(
                        ReportSeverity::error,
                        "io.parse.entity_parameter_value",
                        "Failed to read entity parameter value."));
                return false;
            }
        }
    }

    for (int i = 0; i < constraint_count; ++i) {
        std::uint64_t id = 0;
        double value = 0.0;
        if (!(input >> id >> value)) {
            append_issue(
                result,
                make_issue(
                    ReportSeverity::error,
                    "io.parse.constraint_parameter",
                    "Failed to read constraint parameter block."));
            return false;
        }
        auto* constraint = find_constraint(result.snapshot, kernel::ConstraintId{id});
        if (constraint == nullptr) {
            append_issue(
                result,
                make_issue(
                    ReportSeverity::error,
                    "io.parse.constraint_parameters_missing_constraint",
                    "Constraint parameter block references a missing constraint."));
            return false;
        }
        constraint->value = value;
    }

    return true;
}

}  // namespace

const SceneSchemaRegistry& builtin_schema_registry() {
    static const SceneSchemaRegistry registry = [] {
        SceneSchemaRegistry value;
        value.schemas.push_back(SceneSchemaDescriptor{
            "gcs-0.3",
            SceneFormat::text,
            true,
            true,
            true});
        value.schemas.push_back(SceneSchemaDescriptor{
            "gcs-0.3",
            SceneFormat::json,
            false,
            true,
            true});
        return value;
    }();
    return registry;
}

const SceneSchemaDescriptor* find_schema(const SceneSchemaRegistry& registry,
                                         std::string schema_version,
                                         SceneFormat format) {
    for (const auto& schema : registry.schemas) {
        if (schema.schema_version == schema_version && schema.format == format) {
            return &schema;
        }
    }
    return nullptr;
}

std::string to_string(SceneFormat format) {
    switch (format) {
        case SceneFormat::text: return "text";
        case SceneFormat::json: return "json";
    }
    return "unknown";
}

SceneLoadResult load_scene(const SceneLoadRequest& request) {
    SceneLoadResult result;
    result.format = detect_format(request);

    const auto* schema = find_schema(
        builtin_schema_registry(),
        result.schema_version,
        result.format);
    if (schema == nullptr || !schema->can_read) {
        append_issue(
            result,
            make_issue(
                ReportSeverity::error,
                "io.schema.unsupported_read",
                "Scene schema is not readable by this adapter: " +
                    result.schema_version + " " + to_string(result.format) + "."));
        return result;
    }

    std::ifstream input(request.path);
    if (!input) {
        append_issue(
            result,
            make_issue(
                ReportSeverity::error,
                "io.open_failed",
                "Failed to open scene file: " + request.path));
        return result;
    }

    if (!parse_text_scene(input, result)) {
        return result;
    }

    auto validation = kernel::validate_model(result.snapshot);
    result.validation_report.kernel_report = validation.report;
    result.validation_report.valid = validation.payload.valid;
    if (validation.report.status == kernel::StageStatus::error) {
        for (const auto& message : validation.report.messages) {
            append_issue(
                result,
                make_issue(
                    message.severity,
                    message.code.value,
                    message.summary));
        }
        return result;
    }

    result.canonical_digest = canonical_digest(canonical_text(result.snapshot));
    result.ok = true;
    return result;
}

SceneWriteResult write_scene_text(const SceneWriteRequest& request) {
    SceneWriteResult result;
    result.format = request.format;
    if (request.format != SceneFormat::text) {
        append_issue(
            result,
            make_issue(
                ReportSeverity::error,
                "io.write.unsupported_format",
                "write_scene_text only writes text scenes."));
        return result;
    }

    std::ofstream output(request.path);
    if (!output) {
        append_issue(
            result,
            make_issue(
                ReportSeverity::error,
                "io.write.open_failed",
                "Failed to open scene file for writing: " + request.path));
        return result;
    }

    const std::string bytes = canonical_text(request.snapshot);
    output << bytes;
    if (!output) {
        append_issue(
            result,
            make_issue(
                ReportSeverity::error,
                "io.write.failed",
                "Failed while writing canonical text scene."));
        return result;
    }

    result.canonical_digest = canonical_digest(bytes);
    result.bytes_written = static_cast<int>(bytes.size());
    result.ok = true;
    return result;
}

std::string canonical_text(const ModelSnapshot& snapshot) {
    std::ostringstream output;
    output << std::setprecision(17);

    output << snapshot.rigid_sets.size() << "\n";
    for (const auto& rigid_set : snapshot.rigid_sets) {
        output << rigid_set.id.value << " ";
    }
    output << "\n";

    output << "\n";

    output << snapshot.entities.size() << "\n";
    for (const auto& entity : snapshot.entities) {
        output << entity.id.value << " " << static_cast<int>(entity.kind) << " "
               << entity.rigid_set_id.value << "\n";
    }

    output << snapshot.constraints.size() << "\n";
    for (const auto& constraint : snapshot.constraints) {
        output << constraint.id.value << " " << static_cast<int>(constraint.kind) << " "
               << constraint.entity_ids.size();
        for (kernel::EntityId entity_id : constraint.entity_ids) {
            output << " " << entity_id.value;
        }
        output << "\n";
    }

    output << "\n";
    for (const auto& entity : snapshot.entities) {
        output << entity.id.value;
        for (double value : entity.parameters.values) {
            output << " " << value;
        }
        output << "\n";
    }

    output << "\n";
    for (const auto& constraint : snapshot.constraints) {
        output << constraint.id.value << " " << constraint.value << "\n";
    }

    return output.str();
}

std::string canonical_json(const ModelSnapshot& snapshot) {
    std::ostringstream output;
    output << std::setprecision(17);
    output << "{\n";
    output << "  \"format_version\": \"" << snapshot.schema_version << "\",\n";
    output << "  \"state_version\": " << snapshot.state_version.value << ",\n";
    output << "  \"rigid_sets\": [";
    for (std::size_t i = 0; i < snapshot.rigid_sets.size(); ++i) {
        if (i > 0) output << ", ";
        output << "{\"id\": " << snapshot.rigid_sets[i].id.value << "}";
    }
    output << "],\n";
    output << "  \"geometries\": [";
    for (std::size_t i = 0; i < snapshot.entities.size(); ++i) {
        const auto& entity = snapshot.entities[i];
        if (i > 0) output << ", ";
        output << "{\"id\": " << entity.id.value
               << ", \"type\": " << static_cast<int>(entity.kind)
               << ", \"rigid_set_id\": " << entity.rigid_set_id.value
               << ", \"v\": [";
        for (std::size_t j = 0; j < entity.parameters.values.size(); ++j) {
            if (j > 0) output << ", ";
            output << entity.parameters.values[j];
        }
        output << "]}";
    }
    output << "],\n";
    output << "  \"constraints\": [";
    for (std::size_t i = 0; i < snapshot.constraints.size(); ++i) {
        const auto& constraint = snapshot.constraints[i];
        if (i > 0) output << ", ";
        output << "{\"id\": " << constraint.id.value
               << ", \"type\": " << static_cast<int>(constraint.kind)
               << ", \"geometry_ids\": [";
        for (std::size_t j = 0; j < constraint.entity_ids.size(); ++j) {
            if (j > 0) output << ", ";
            output << constraint.entity_ids[j].value;
        }
        output << "], \"value\": " << constraint.value << "}";
    }
    output << "]\n";
    output << "}\n";
    return output.str();
}

CanonicalDigest canonical_digest(const std::string& bytes) {
    std::uint64_t hash = 1469598103934665603ULL;
    for (unsigned char byte : bytes) {
        hash ^= static_cast<std::uint64_t>(byte);
        hash *= 1099511628211ULL;
    }

    std::ostringstream value;
    value << std::hex << std::setw(16) << std::setfill('0') << hash;

    CanonicalDigest digest;
    digest.value = value.str();
    digest.byte_count = static_cast<int>(bytes.size());
    return digest;
}

gcs::kernel::ContractResult<RoundTripDiffReport> round_trip(
    SceneRoundTripRequest request) {
    kernel::ContractResult<RoundTripDiffReport> result;
    result.report = kernel::make_stage_report("io_adapters.round_trip");

    std::string bytes;
    if (request.format == SceneFormat::text) {
        bytes = canonical_text(request.snapshot);
    } else {
        bytes = canonical_json(request.snapshot);
    }
    result.payload.before_digest = canonical_digest(bytes);

    if (request.format != SceneFormat::text) {
        kernel::append_report_message(
            result.report,
            kernel::make_report_message(
                ReportSeverity::error,
                kernel::ReportCode{"io.round_trip.unsupported_format"},
                "Round-trip parsing currently supports text scenes only."));
        return result;
    }

    SceneLoadResult loaded;
    std::istringstream input(bytes);
    if (!parse_text_scene(input, loaded)) {
        for (const auto& issue : loaded.parse_issues) {
            kernel::append_report_message(
                result.report,
                kernel::make_report_message(
                    issue.severity,
                    kernel::ReportCode{issue.code},
                    issue.message));
        }
        return result;
    }

    result.payload.loaded_snapshot = loaded.snapshot;
    result.payload.after_digest = canonical_digest(canonical_text(loaded.snapshot));
    auto diff = kernel::diff_snapshots(request.snapshot, loaded.snapshot);
    result.payload.changed_entities = diff.payload.changed_entities;
    result.payload.changed_constraints = diff.payload.added_constraints;
    for (auto constraint_id : diff.payload.removed_constraints) {
        result.payload.changed_constraints.push_back(constraint_id);
    }
    result.payload.equivalent =
        result.payload.before_digest.value == result.payload.after_digest.value &&
        result.payload.changed_entities.empty() &&
        result.payload.changed_constraints.empty();
    return result;
}

std::string summarize_scene(const ModelSnapshot& snapshot) {
    std::ostringstream output;
    output << "StateVersion=" << snapshot.state_version.value
           << " RigidSets=" << snapshot.rigid_sets.size()
           << " Entities=" << snapshot.entities.size()
           << " Constraints=" << snapshot.constraints.size();
    return output.str();
}

}
