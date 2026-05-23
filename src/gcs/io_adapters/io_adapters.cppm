module;

#include <string>
#include <vector>

export module gcs.io_adapters;

export import gcs.kernel;

export namespace gcs::io {

using gcs::kernel::ModelSnapshot;
using gcs::kernel::ReportSeverity;
using gcs::kernel::StageReport;

enum class SceneFormat {
    text,
    json,
};

enum class CompatibilityMode {
    strict,
    migration_allowed,
};

struct SceneSchemaDescriptor {
    std::string schema_version = "gcs-0.3";
    SceneFormat format = SceneFormat::text;
    bool can_read = true;
    bool can_write = true;
    bool current = true;
};

struct SceneSchemaRegistry {
    std::vector<SceneSchemaDescriptor> schemas;
};

struct ParseIssue {
    ReportSeverity severity = ReportSeverity::error;
    std::string code;
    std::string message;
    int line = 0;
    int column = 0;
};

struct SceneValidationReport {
    bool valid = true;
    StageReport kernel_report;
    std::vector<ParseIssue> issues;
};

struct SceneMigrationReport {
    bool migrated = false;
    std::string from_schema_version;
    std::string to_schema_version;
    std::vector<ParseIssue> issues;
};

struct CanonicalDigest {
    std::string algorithm = "fnv1a64";
    std::string value;
    int byte_count = 0;
};

struct SceneLoadRequest {
    std::string path;
    SceneFormat format = SceneFormat::text;
    bool auto_detect_format = true;
    CompatibilityMode compatibility = CompatibilityMode::strict;
};

struct SceneLoadResult {
    bool ok = false;
    ModelSnapshot snapshot;
    std::vector<std::string> errors;
    SceneFormat format = SceneFormat::text;
    std::string schema_version = "gcs-0.3";
    SceneValidationReport validation_report;
    SceneMigrationReport migration_report;
    CanonicalDigest canonical_digest;
    std::vector<ParseIssue> parse_issues;
};

struct SceneWriteRequest {
    std::string path;
    ModelSnapshot snapshot;
    SceneFormat format = SceneFormat::text;
    CompatibilityMode compatibility = CompatibilityMode::strict;
};

struct SceneWriteResult {
    bool ok = false;
    std::vector<std::string> errors;
    SceneFormat format = SceneFormat::text;
    std::string schema_version = "gcs-0.3";
    CanonicalDigest canonical_digest;
    int bytes_written = 0;
    std::vector<ParseIssue> issues;
};

struct SceneRoundTripRequest {
    ModelSnapshot snapshot;
    SceneFormat format = SceneFormat::text;
};

struct RoundTripDiffReport {
    bool equivalent = false;
    CanonicalDigest before_digest;
    CanonicalDigest after_digest;
    std::vector<gcs::kernel::EntityId> changed_entities;
    std::vector<gcs::kernel::ConstraintId> changed_constraints;
    ModelSnapshot loaded_snapshot;
};

const SceneSchemaRegistry& builtin_schema_registry();
const SceneSchemaDescriptor* find_schema(const SceneSchemaRegistry& registry,
                                         std::string schema_version,
                                         SceneFormat format);
std::string to_string(SceneFormat format);
SceneLoadResult load_scene(const SceneLoadRequest& request);
SceneWriteResult write_scene_text(const SceneWriteRequest& request);
std::string canonical_text(const ModelSnapshot& snapshot);
std::string canonical_json(const ModelSnapshot& snapshot);
CanonicalDigest canonical_digest(const std::string& bytes);
gcs::kernel::ContractResult<RoundTripDiffReport> round_trip(
    SceneRoundTripRequest request);
std::string summarize_scene(const ModelSnapshot& snapshot);

}
