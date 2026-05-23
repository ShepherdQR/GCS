import gcs.contract_tools;
import gcs.io_adapters;
import gcs.kernel;

#include <gtest/gtest.h>

#include <string>
#include <vector>

namespace {

namespace io = gcs::io;

std::string source_path(const char* path) {
    return std::string(GCS_SOURCE_DIR) + "/" + path;
}

bool has_issue_code(const std::vector<io::ParseIssue>& issues, const char* code) {
    for (const auto& issue : issues) {
        if (issue.code == code) return true;
    }
    return false;
}

}  // namespace

TEST(IoAdaptersContract, LoadsCurrentTextSchemaFixture) {
    auto result = io::load_scene(
        io::SceneLoadRequest{source_path("fixtures/scene/basic/g1.txt")});

    ASSERT_TRUE(result.ok);
    EXPECT_EQ(result.format, io::SceneFormat::text);
    EXPECT_EQ(result.schema_version, "gcs-0.3");
    EXPECT_TRUE(result.validation_report.valid);
    EXPECT_FALSE(result.canonical_digest.value.empty());
    EXPECT_EQ(result.snapshot.entities.size(), 5U);
    EXPECT_EQ(result.snapshot.constraints.size(), 2U);
}

TEST(IoAdaptersContract, LoadsCurrentJsonSchemaFixture) {
    auto result = io::load_scene(
        io::SceneLoadRequest{source_path("fixtures/scene/json/current_two_point.gcs.json")});

    ASSERT_TRUE(result.ok);
    EXPECT_EQ(result.format, io::SceneFormat::json);
    EXPECT_EQ(result.schema_version, "gcs-0.3");
    EXPECT_TRUE(result.validation_report.valid);
    EXPECT_FALSE(result.canonical_digest.value.empty());
    EXPECT_EQ(result.snapshot.entities.size(), 2U);
    EXPECT_EQ(result.snapshot.constraints.size(), 1U);
    EXPECT_EQ(result.snapshot.constraints.front().entity_ids.front().value, 0U);
}

TEST(IoAdaptersContract, MigratesLegacyJsonSchemaFixture) {
    io::SceneLoadRequest request{
        source_path("fixtures/scene/json/legacy_two_point_v02.gcs.json")};
    request.compatibility = io::CompatibilityMode::migration_allowed;

    auto result = io::load_scene(request);

    ASSERT_TRUE(result.ok);
    EXPECT_EQ(result.schema_version, "gcs-0.3");
    EXPECT_TRUE(result.migration_report.migrated);
    EXPECT_EQ(result.migration_report.from_schema_version, "gcs-0.2");
    EXPECT_EQ(result.migration_report.to_schema_version, "gcs-0.3");
    ASSERT_FALSE(result.migration_report.issues.empty());
    EXPECT_EQ(result.migration_report.issues.front().code, "io.migration.gcs_0_2_to_0_3");
    EXPECT_EQ(result.snapshot.entities.size(), 2U);
    EXPECT_EQ(result.snapshot.constraints.front().entity_ids.back().value, 1U);
}

TEST(IoAdaptersContract, RejectsMalformedJsonWithTypedIssue) {
    auto result = io::load_scene(
        io::SceneLoadRequest{source_path("fixtures/scene/json/malformed.gcs.json")});

    EXPECT_FALSE(result.ok);
    EXPECT_EQ(result.format, io::SceneFormat::json);
    EXPECT_TRUE(has_issue_code(result.parse_issues, "io.json.parse_error") ||
                has_issue_code(result.parse_issues, "io.json.object") ||
                has_issue_code(result.parse_issues, "io.json.array"));
    ASSERT_FALSE(result.errors.empty());
}

TEST(IoAdaptersContract, CanonicalTextDigestIsDeterministic) {
    auto model = gcs::tools::make_two_point_distance_model();

    const auto first_text = io::canonical_text(model);
    const auto second_text = io::canonical_text(model);
    const auto first_digest = io::canonical_digest(first_text);
    const auto second_digest = io::canonical_digest(second_text);

    EXPECT_EQ(first_text, second_text);
    EXPECT_EQ(first_digest.value, second_digest.value);
    EXPECT_EQ(first_digest.byte_count, static_cast<int>(first_text.size()));
}

TEST(IoAdaptersContract, CanonicalJsonPathIsDeterministic) {
    auto model = gcs::tools::make_two_point_distance_model();

    const auto first_json = io::canonical_json(model);
    const auto second_json = io::canonical_json(model);

    EXPECT_EQ(first_json, second_json);
    EXPECT_NE(first_json.find("\"format_version\""), std::string::npos);
    EXPECT_NE(first_json.find("\"geometries\""), std::string::npos);
    EXPECT_NE(first_json.find("\"constraints\""), std::string::npos);
}

TEST(IoAdaptersContract, RoundTripPreservesStableIds) {
    auto model = gcs::tools::make_two_point_distance_model();

    auto result = io::round_trip(io::SceneRoundTripRequest{model, io::SceneFormat::text});

    EXPECT_TRUE(result.payload.equivalent);
    EXPECT_EQ(result.payload.before_digest.value, result.payload.after_digest.value);
    EXPECT_TRUE(result.payload.changed_entities.empty());
    EXPECT_TRUE(result.payload.changed_constraints.empty());
    ASSERT_EQ(result.payload.loaded_snapshot.entities.size(), model.entities.size());
    EXPECT_EQ(result.payload.loaded_snapshot.entities.front().id.value,
              model.entities.front().id.value);
}

TEST(IoAdaptersContract, JsonRoundTripPreservesStableIds) {
    auto model = gcs::tools::make_two_point_distance_model();

    auto result = io::round_trip(io::SceneRoundTripRequest{model, io::SceneFormat::json});

    EXPECT_TRUE(result.payload.equivalent);
    EXPECT_EQ(result.payload.before_digest.value, result.payload.after_digest.value);
    EXPECT_TRUE(result.payload.changed_entities.empty());
    EXPECT_TRUE(result.payload.changed_constraints.empty());
    ASSERT_EQ(result.payload.loaded_snapshot.entities.size(), model.entities.size());
    EXPECT_EQ(result.payload.loaded_snapshot.constraints.front().value,
              model.constraints.front().value);
}

TEST(IoAdaptersContract, SchemaRegistryNamesTextAndJsonPaths) {
    const auto& registry = io::builtin_schema_registry();

    const auto* text = io::find_schema(registry, "gcs-0.3", io::SceneFormat::text);
    const auto* json = io::find_schema(registry, "gcs-0.3", io::SceneFormat::json);

    ASSERT_NE(text, nullptr);
    ASSERT_NE(json, nullptr);
    EXPECT_TRUE(text->can_read);
    EXPECT_TRUE(text->can_write);
    EXPECT_TRUE(json->can_read);
    EXPECT_TRUE(json->can_write);
}
