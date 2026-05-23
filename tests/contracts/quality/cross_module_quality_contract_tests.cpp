import gcs.contract_tools;
import gcs.diagnostics;
import gcs.io_adapters;
import gcs.kernel;
import gcs.session_runtime;
import gcs.viewer_bridge;

#include <gtest/gtest.h>

#include <vector>

namespace {

namespace diagnostics = gcs::diagnostics;
namespace io = gcs::io;
namespace kernel = gcs::kernel;
namespace runtime = gcs::runtime;
namespace tools = gcs::tools;
namespace viewer = gcs::viewer;

bool stage_reports_have_code(const std::vector<kernel::StageReport>& reports,
                             const char* code) {
    for (const auto& report : reports) {
        for (const auto& message : report.messages) {
            if (message.code.value == code) return true;
        }
    }
    return false;
}

bool parse_issues_have_code(const std::vector<io::ParseIssue>& issues,
                            const char* code) {
    for (const auto& issue : issues) {
        if (issue.code == code) return true;
    }
    return false;
}

bool overlay_has_code(const viewer::DiagnosticOverlay& overlay, const char* code) {
    for (const auto& item : overlay.items) {
        if (item.code == code) return true;
    }
    return false;
}

kernel::LocalSection make_section(const kernel::ModelSnapshot& model,
                                  kernel::ContextId context_id,
                                  double x_offset) {
    kernel::LocalSection section;
    section.context_id = context_id;
    section.valid = true;
    section.entity_states = kernel::capture_entity_states(model, {kernel::EntityId{0}});
    section.entity_states.front().parameters.values[0] += x_offset;
    return section;
}

}  // namespace

TEST(CrossModuleQualityContract, InvalidModelRollbackNamesStableKernelFailure) {
    auto fixture = tools::build_fixture(
        tools::FixtureBuildRequest{tools::FixtureKind::missing_entity_reference, 404});
    runtime::SessionRuntime session(fixture.payload.model);

    auto result = session.solve();

    EXPECT_FALSE(result.accepted);
    EXPECT_EQ(result.user_visible_status, kernel::SolveStatus::invalid_model);
    EXPECT_TRUE(result.rollback_report.rolled_back);
    EXPECT_EQ(session.current_snapshot().state_version.value, 0U);
    EXPECT_TRUE(stage_reports_have_code(result.stage_reports, "kernel.missing_entity"));
    EXPECT_EQ(fixture.payload.provenance.fixture_id, "missing_entity_reference");
}

TEST(CrossModuleQualityContract, UnsupportedJsonSceneReportsTypedParseIssue) {
    auto result = io::load_scene(io::SceneLoadRequest{"negative_corpus/unsupported.json"});

    EXPECT_FALSE(result.ok);
    EXPECT_EQ(result.format, io::SceneFormat::json);
    EXPECT_TRUE(parse_issues_have_code(result.parse_issues, "io.schema.unsupported_read"));
}

TEST(CrossModuleQualityContract, GluingObstructionPropagatesToViewerOverlay) {
    auto fixture = tools::build_fixture(
        tools::FixtureBuildRequest{tools::FixtureKind::two_point_distance, 0});
    auto source = make_section(fixture.payload.model, kernel::ContextId{1}, 0.0);
    auto target = make_section(fixture.payload.model, kernel::ContextId{2}, 1.0);

    kernel::BoundaryProjection projection;
    projection.id = kernel::ProjectionId{9};
    projection.source_context_id = source.context_id;
    projection.target_context_id = target.context_id;
    projection.entity_ids = {kernel::EntityId{0}};
    projection.constraint_ids = {kernel::ConstraintId{0}};

    auto gluing = diagnostics::glue_local_sections(
        diagnostics::GluingInput{
            fixture.payload.model,
            {},
            {source, target},
            {projection},
            {},
            fixture.payload.model.tolerances});

    runtime::CommandResult command_result;
    command_result.user_visible_status = kernel::SolveStatus::inconsistent;
    command_result.gluing_report = gluing;
    command_result.obstruction_report = gluing.obstruction_report;
    command_result.stage_reports.push_back(gluing.stage_report);

    auto overlay = viewer::build_overlay(
        viewer::DiagnosticOverlayRequest{
            fixture.payload.model,
            command_result,
            viewer::DiagnosticVerbosity::detailed});

    EXPECT_FALSE(gluing.accepted);
    EXPECT_TRUE(gluing.obstruction_report.present);
    EXPECT_TRUE(overlay_has_code(overlay.payload, "gluing.boundary_projection_mismatch"));
}

TEST(CrossModuleQualityContract, RoundTripRuntimeAndViewerShareStableState) {
    auto fixture = tools::build_fixture(
        tools::FixtureBuildRequest{tools::FixtureKind::two_point_distance, 11});
    auto round_trip = io::round_trip(
        io::SceneRoundTripRequest{fixture.payload.model, io::SceneFormat::text});
    ASSERT_TRUE(round_trip.payload.equivalent);

    runtime::SessionRuntime session(round_trip.payload.loaded_snapshot);
    auto result = session.solve();
    auto projection = viewer::project_scene(
        viewer::ViewerProjectionRequest{session.current_snapshot()});

    EXPECT_TRUE(result.accepted);
    EXPECT_EQ(session.current_snapshot().state_version.value, 1U);
    EXPECT_EQ(projection.payload.state_version.value, 1U);
    EXPECT_EQ(projection.payload.entities.size(), fixture.payload.model.entities.size());
}

TEST(CrossModuleQualityContract, NegativeFixtureInvariantReportUsesProvenance) {
    auto fixture = tools::build_fixture(
        tools::FixtureBuildRequest{tools::FixtureKind::missing_entity_reference, 515});

    auto invariants = tools::check_invariants(
        tools::InvariantCheckRequest{fixture.payload.model, fixture.payload.whole_context});

    EXPECT_EQ(fixture.payload.provenance.deterministic_seed, 515);
    EXPECT_EQ(fixture.payload.provenance.fixture_id, "missing_entity_reference");
    EXPECT_FALSE(invariants.payload.valid);
    EXPECT_FALSE(invariants.payload.messages.empty());
}
