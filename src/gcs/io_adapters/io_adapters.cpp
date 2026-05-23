module;

#include <cstdint>
#include <cstddef>
#include <cmath>
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

struct JsonValue {
    enum class Kind {
        null_value,
        number,
        string,
        object,
        array,
    };

    Kind kind = Kind::null_value;
    double number = 0.0;
    std::string string;
    std::vector<std::pair<std::string, JsonValue>> object;
    std::vector<JsonValue> array;
};

class JsonParser {
public:
    JsonParser(const std::string& text, SceneLoadResult& result)
        : text_(text), result_(result) {}

    bool parse(JsonValue& value) {
        skip_whitespace();
        if (!parse_value(value)) return false;
        skip_whitespace();
        if (position_ != text_.size()) {
            fail("io.json.trailing_content", "JSON document has trailing content.");
            return false;
        }
        return true;
    }

private:
    const std::string& text_;
    SceneLoadResult& result_;
    std::size_t position_ = 0;
    int line_ = 1;
    int column_ = 1;

    bool at_end() const {
        return position_ >= text_.size();
    }

    char peek() const {
        return at_end() ? '\0' : text_[position_];
    }

    char advance() {
        const char value = peek();
        if (!at_end()) {
            ++position_;
            if (value == '\n') {
                ++line_;
                column_ = 1;
            } else {
                ++column_;
            }
        }
        return value;
    }

    void skip_whitespace() {
        while (!at_end()) {
            const char value = peek();
            if (value != ' ' && value != '\n' && value != '\r' && value != '\t') {
                break;
            }
            advance();
        }
    }

    void fail(const char* code, const std::string& message) {
        append_issue(
            result_,
            make_issue(
                ReportSeverity::error,
                code,
                message,
                line_,
                column_));
    }

    bool consume(char expected, const char* code, const char* message) {
        if (peek() != expected) {
            fail(code, message);
            return false;
        }
        advance();
        return true;
    }

    bool parse_value(JsonValue& value) {
        skip_whitespace();
        if (at_end()) {
            fail("io.json.unexpected_end", "Unexpected end of JSON document.");
            return false;
        }

        switch (peek()) {
            case '{': return parse_object(value);
            case '[': return parse_array(value);
            case '"': return parse_string_value(value);
            case 'n': return parse_literal("null", JsonValue::Kind::null_value, value);
            default:
                if (peek() == '-' || (peek() >= '0' && peek() <= '9')) {
                    return parse_number(value);
                }
                fail("io.json.parse_error", "Unexpected token while parsing JSON value.");
                return false;
        }
    }

    bool parse_literal(const char* literal, JsonValue::Kind kind, JsonValue& value) {
        for (const char* current = literal; *current != '\0'; ++current) {
            if (peek() != *current) {
                fail("io.json.parse_error", "Invalid JSON literal.");
                return false;
            }
            advance();
        }
        value.kind = kind;
        return true;
    }

    bool parse_string(std::string& output) {
        if (!consume('"', "io.json.string", "Expected JSON string.")) return false;
        output.clear();
        while (!at_end()) {
            const char value = advance();
            if (value == '"') return true;
            if (value == '\\') {
                if (at_end()) {
                    fail("io.json.string_escape", "Unterminated JSON string escape.");
                    return false;
                }
                const char escaped = advance();
                switch (escaped) {
                    case '"': output.push_back('"'); break;
                    case '\\': output.push_back('\\'); break;
                    case '/': output.push_back('/'); break;
                    case 'b': output.push_back('\b'); break;
                    case 'f': output.push_back('\f'); break;
                    case 'n': output.push_back('\n'); break;
                    case 'r': output.push_back('\r'); break;
                    case 't': output.push_back('\t'); break;
                    default:
                        fail("io.json.string_escape", "Unsupported JSON string escape.");
                        return false;
                }
            } else {
                output.push_back(value);
            }
        }
        fail("io.json.string", "Unterminated JSON string.");
        return false;
    }

    bool parse_string_value(JsonValue& value) {
        value.kind = JsonValue::Kind::string;
        return parse_string(value.string);
    }

    bool parse_number(JsonValue& value) {
        const std::size_t start = position_;
        if (peek() == '-') advance();
        if (peek() < '0' || peek() > '9') {
            fail("io.json.number", "Invalid JSON number.");
            return false;
        }
        while (peek() >= '0' && peek() <= '9') advance();
        if (peek() == '.') {
            advance();
            if (peek() < '0' || peek() > '9') {
                fail("io.json.number", "Invalid JSON number fraction.");
                return false;
            }
            while (peek() >= '0' && peek() <= '9') advance();
        }
        if (peek() == 'e' || peek() == 'E') {
            advance();
            if (peek() == '+' || peek() == '-') advance();
            if (peek() < '0' || peek() > '9') {
                fail("io.json.number", "Invalid JSON number exponent.");
                return false;
            }
            while (peek() >= '0' && peek() <= '9') advance();
        }

        value.kind = JsonValue::Kind::number;
        value.number = std::stod(text_.substr(start, position_ - start));
        return true;
    }

    bool parse_array(JsonValue& value) {
        if (!consume('[', "io.json.array", "Expected JSON array.")) return false;
        value.kind = JsonValue::Kind::array;
        value.array.clear();
        skip_whitespace();
        if (peek() == ']') {
            advance();
            return true;
        }
        while (!at_end()) {
            JsonValue element;
            if (!parse_value(element)) return false;
            value.array.push_back(std::move(element));
            skip_whitespace();
            if (peek() == ']') {
                advance();
                return true;
            }
            if (!consume(',', "io.json.array", "Expected comma in JSON array.")) {
                return false;
            }
        }
        fail("io.json.array", "Unterminated JSON array.");
        return false;
    }

    bool parse_object(JsonValue& value) {
        if (!consume('{', "io.json.object", "Expected JSON object.")) return false;
        value.kind = JsonValue::Kind::object;
        value.object.clear();
        skip_whitespace();
        if (peek() == '}') {
            advance();
            return true;
        }
        while (!at_end()) {
            std::string key;
            if (!parse_string(key)) return false;
            skip_whitespace();
            if (!consume(':', "io.json.object", "Expected ':' after JSON object key.")) {
                return false;
            }
            JsonValue element;
            if (!parse_value(element)) return false;
            value.object.push_back({std::move(key), std::move(element)});
            skip_whitespace();
            if (peek() == '}') {
                advance();
                return true;
            }
            if (!consume(',', "io.json.object", "Expected comma in JSON object.")) {
                return false;
            }
            skip_whitespace();
        }
        fail("io.json.object", "Unterminated JSON object.");
        return false;
    }
};

const JsonValue* object_field(const JsonValue& value, const char* name) {
    if (value.kind != JsonValue::Kind::object) return nullptr;
    for (const auto& field : value.object) {
        if (field.first == name) return &field.second;
    }
    return nullptr;
}

bool require_object(const JsonValue& value,
                    SceneLoadResult& result,
                    const char* code,
                    const char* message) {
    if (value.kind == JsonValue::Kind::object) return true;
    append_issue(result, make_issue(ReportSeverity::error, code, message));
    return false;
}

bool read_string_field(const JsonValue& object,
                       const char* name,
                       std::string& output,
                       SceneLoadResult& result,
                       bool required = true) {
    const auto* field = object_field(object, name);
    if (field == nullptr) {
        if (required) {
            append_issue(
                result,
                make_issue(
                    ReportSeverity::error,
                    "io.json.missing_field",
                    std::string("Missing JSON string field: ") + name));
        }
        return false;
    }
    if (field->kind != JsonValue::Kind::string) {
        append_issue(
            result,
            make_issue(
                ReportSeverity::error,
                "io.json.invalid_field_type",
                std::string("JSON field must be a string: ") + name));
        return false;
    }
    output = field->string;
    return true;
}

bool read_number_field(const JsonValue& object,
                       const char* name,
                       double& output,
                       SceneLoadResult& result,
                       bool required = true) {
    const auto* field = object_field(object, name);
    if (field == nullptr) {
        if (required) {
            append_issue(
                result,
                make_issue(
                    ReportSeverity::error,
                    "io.json.missing_field",
                    std::string("Missing JSON number field: ") + name));
        }
        return false;
    }
    if (field->kind != JsonValue::Kind::number) {
        append_issue(
            result,
            make_issue(
                ReportSeverity::error,
                "io.json.invalid_field_type",
                std::string("JSON field must be a number: ") + name));
        return false;
    }
    output = field->number;
    return true;
}

bool read_uint_field(const JsonValue& object,
                     const char* name,
                     std::uint64_t& output,
                     SceneLoadResult& result,
                     bool required = true) {
    double value = 0.0;
    if (!read_number_field(object, name, value, result, required)) return !required;
    if (value < 0.0 || std::floor(value) != value) {
        append_issue(
            result,
            make_issue(
                ReportSeverity::error,
                "io.json.invalid_integer",
                std::string("JSON field must be a non-negative integer: ") + name));
        return false;
    }
    output = static_cast<std::uint64_t>(value);
    return true;
}

const JsonValue* read_array_field(const JsonValue& object,
                                  const char* name,
                                  SceneLoadResult& result,
                                  bool required = true) {
    const auto* field = object_field(object, name);
    if (field == nullptr) {
        if (required) {
            append_issue(
                result,
                make_issue(
                    ReportSeverity::error,
                    "io.json.missing_field",
                    std::string("Missing JSON array field: ") + name));
        }
        return nullptr;
    }
    if (field->kind != JsonValue::Kind::array) {
        append_issue(
            result,
            make_issue(
                ReportSeverity::error,
                "io.json.invalid_field_type",
                std::string("JSON field must be an array: ") + name));
        return nullptr;
    }
    return field;
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

bool parse_entity_ids_array(const JsonValue& array,
                            std::vector<kernel::EntityId>& entity_ids,
                            SceneLoadResult& result,
                            const char* field_name) {
    if (array.kind != JsonValue::Kind::array) {
        append_issue(
            result,
            make_issue(
                ReportSeverity::error,
                "io.json.invalid_field_type",
                std::string("JSON field must be an array: ") + field_name));
        return false;
    }

    for (const auto& element : array.array) {
        if (element.kind != JsonValue::Kind::number ||
            element.number < 0.0 ||
            std::floor(element.number) != element.number) {
            append_issue(
                result,
                make_issue(
                    ReportSeverity::error,
                    "io.json.invalid_integer",
                    std::string("JSON ID array contains a non-integer value: ") +
                        field_name));
            return false;
        }
        entity_ids.push_back(kernel::EntityId{
            static_cast<std::uint64_t>(element.number)});
    }
    return true;
}

bool parse_parameter_array(const JsonValue& object,
                           kernel::EntityDraft& entity,
                           SceneLoadResult& result,
                           CompatibilityMode compatibility) {
    const JsonValue* parameters = object_field(object, "v");
    if (parameters == nullptr && compatibility == CompatibilityMode::migration_allowed) {
        parameters = object_field(object, "parameters");
    }
    if (parameters == nullptr) {
        append_issue(
            result,
            make_issue(
                ReportSeverity::error,
                "io.json.missing_field",
                "Geometry JSON object is missing parameter array field: v."));
        return false;
    }
    if (parameters->kind != JsonValue::Kind::array) {
        append_issue(
            result,
            make_issue(
                ReportSeverity::error,
                "io.json.invalid_field_type",
                "Geometry parameter field must be an array."));
        return false;
    }
    if (parameters->array.size() < static_cast<std::size_t>(entity.parameters.dimension)) {
        append_issue(
            result,
            make_issue(
                ReportSeverity::error,
                "io.json.parameter_dimension",
                "Geometry parameter array is shorter than the geometry DOF."));
        return false;
    }
    for (std::size_t index = 0; index < parameters->array.size() &&
                                index < entity.parameters.values.size();
         ++index) {
        const auto& value = parameters->array[index];
        if (value.kind != JsonValue::Kind::number) {
            append_issue(
                result,
                make_issue(
                    ReportSeverity::error,
                    "io.json.invalid_field_type",
                    "Geometry parameter value must be numeric."));
            return false;
        }
        entity.parameters.values[index] = value.number;
    }
    return true;
}

void populate_rigid_set_memberships(ModelSnapshot& snapshot) {
    for (auto& rigid_set : snapshot.rigid_sets) {
        rigid_set.entity_ids.clear();
    }
    for (const auto& entity : snapshot.entities) {
        for (auto& rigid_set : snapshot.rigid_sets) {
            if (rigid_set.id == entity.rigid_set_id) {
                rigid_set.entity_ids.push_back(entity.id);
                break;
            }
        }
    }
}

bool parse_json_scene_bytes(const std::string& bytes,
                            SceneLoadResult& result,
                            CompatibilityMode compatibility) {
    JsonValue root;
    JsonParser parser(bytes, result);
    if (!parser.parse(root)) return false;
    if (!require_object(
            root,
            result,
            "io.json.root",
            "JSON scene root must be an object.")) {
        return false;
    }

    std::string schema_version;
    bool used_legacy_schema_field = false;
    if (!read_string_field(root, "format_version", schema_version, result, false)) {
        used_legacy_schema_field =
            read_string_field(root, "schema_version", schema_version, result, false);
    }
    if (schema_version.empty()) {
        append_issue(
            result,
            make_issue(
                ReportSeverity::error,
                "io.schema.missing_format_version",
                "JSON scene must declare format_version."));
        return false;
    }

    result.schema_version = schema_version;
    result.snapshot.schema_version = schema_version;
    if (schema_version != "gcs-0.3") {
        if (compatibility != CompatibilityMode::migration_allowed ||
            schema_version != "gcs-0.2") {
            append_issue(
                result,
                make_issue(
                    ReportSeverity::error,
                    "io.schema.unsupported_version",
                    "JSON scene schema is not supported: " + schema_version));
            return false;
        }
        result.migration_report.migrated = true;
        result.migration_report.from_schema_version = schema_version;
        result.migration_report.to_schema_version = "gcs-0.3";
        result.snapshot.schema_version = "gcs-0.3";
        result.schema_version = "gcs-0.3";
        result.migration_report.issues.push_back(
            make_issue(
                ReportSeverity::warning,
                "io.migration.gcs_0_2_to_0_3",
                "Migrated JSON scene from gcs-0.2 to gcs-0.3."));
    } else if (used_legacy_schema_field &&
               compatibility == CompatibilityMode::migration_allowed) {
        result.migration_report.migrated = true;
        result.migration_report.from_schema_version = "gcs-0.3";
        result.migration_report.to_schema_version = "gcs-0.3";
        result.migration_report.issues.push_back(
            make_issue(
                ReportSeverity::warning,
                "io.migration.schema_version_field",
                "Migrated legacy schema_version field to format_version."));
    }

    double state_version = 0.0;
    if (read_number_field(root, "state_version", state_version, result, false)) {
        if (state_version < 0.0 || std::floor(state_version) != state_version) {
            append_issue(
                result,
                make_issue(
                    ReportSeverity::error,
                    "io.json.invalid_integer",
                    "state_version must be a non-negative integer."));
            return false;
        }
        result.snapshot.state_version = kernel::StateVersionId{
            static_cast<std::uint64_t>(state_version)};
    }

    const auto* rigid_sets = read_array_field(root, "rigid_sets", result);
    const auto* geometries = read_array_field(root, "geometries", result);
    const auto* constraints = read_array_field(root, "constraints", result);
    if (rigid_sets == nullptr || geometries == nullptr || constraints == nullptr) {
        return false;
    }

    for (const auto& value : rigid_sets->array) {
        if (!require_object(
                value,
                result,
                "io.json.rigid_set",
                "Rigid set entry must be an object.")) {
            return false;
        }
        std::uint64_t id = 0;
        if (!read_uint_field(value, "id", id, result)) return false;
        result.snapshot.rigid_sets.push_back(
            kernel::RigidSetDraft{kernel::RigidSetId{id}, {}});
    }

    for (const auto& value : geometries->array) {
        if (!require_object(
                value,
                result,
                "io.json.geometry",
                "Geometry entry must be an object.")) {
            return false;
        }
        std::uint64_t id = 0;
        std::uint64_t type = 0;
        std::uint64_t rigid_set_id = 0;
        if (!read_uint_field(value, "id", id, result) ||
            !read_uint_field(value, "type", type, result) ||
            !read_uint_field(value, "rigid_set_id", rigid_set_id, result)) {
            return false;
        }

        kernel::EntityDraft entity;
        entity.id = kernel::EntityId{id};
        entity.kind = static_cast<kernel::GeometryKind>(type);
        entity.rigid_set_id = kernel::RigidSetId{rigid_set_id};
        entity.parameters.dimension = kernel::geometry_dof(entity.kind);
        if (!parse_parameter_array(value, entity, result, compatibility)) return false;
        result.snapshot.entities.push_back(entity);
    }

    for (const auto& value : constraints->array) {
        if (!require_object(
                value,
                result,
                "io.json.constraint",
                "Constraint entry must be an object.")) {
            return false;
        }
        std::uint64_t id = 0;
        std::uint64_t type = 0;
        double constraint_value = 0.0;
        if (!read_uint_field(value, "id", id, result) ||
            !read_uint_field(value, "type", type, result)) {
            return false;
        }
        if (!read_number_field(value, "value", constraint_value, result)) return false;

        const JsonValue* entity_ids = object_field(value, "geometry_ids");
        if (entity_ids == nullptr && compatibility == CompatibilityMode::migration_allowed) {
            entity_ids = object_field(value, "entity_ids");
        }
        if (entity_ids == nullptr) {
            append_issue(
                result,
                make_issue(
                    ReportSeverity::error,
                    "io.json.missing_field",
                    "Constraint JSON object is missing geometry_ids."));
            return false;
        }

        kernel::ConstraintDraft constraint;
        constraint.id = kernel::ConstraintId{id};
        constraint.kind = static_cast<kernel::ConstraintKind>(type);
        constraint.value = constraint_value;
        if (!parse_entity_ids_array(
                *entity_ids,
                constraint.entity_ids,
                result,
                "geometry_ids")) {
            return false;
        }
        result.snapshot.constraints.push_back(std::move(constraint));
    }

    populate_rigid_set_memberships(result.snapshot);
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
            true,
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

    if (result.format == SceneFormat::json) {
        std::ostringstream bytes;
        bytes << input.rdbuf();
        if (!parse_json_scene_bytes(bytes.str(), result, request.compatibility)) {
            return result;
        }
    } else if (!parse_text_scene(input, result)) {
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

    result.canonical_digest = canonical_digest(
        result.format == SceneFormat::json
            ? canonical_json(result.snapshot)
            : canonical_text(result.snapshot));
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

    SceneLoadResult loaded;
    bool parsed = false;
    if (request.format == SceneFormat::json) {
        loaded.format = SceneFormat::json;
        parsed = parse_json_scene_bytes(bytes, loaded, CompatibilityMode::strict);
    } else {
        std::istringstream input(bytes);
        parsed = parse_text_scene(input, loaded);
    }
    if (!parsed) {
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
    result.payload.after_digest = canonical_digest(
        request.format == SceneFormat::json
            ? canonical_json(loaded.snapshot)
            : canonical_text(loaded.snapshot));
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
