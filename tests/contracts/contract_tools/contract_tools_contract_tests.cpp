import gcs.contract_tools;
import gcs.diagnostics;
import gcs.kernel;
import gcs.numeric_engine;

#include <gtest/gtest.h>

#include <string>
#include <vector>

namespace {

namespace kernel = gcs::kernel;
namespace diagnostics = gcs::diagnostics;
namespace numeric = gcs::numeric;
namespace tools = gcs::tools;

bool has_message_code(const std::vector<kernel::ReportMessage>& messages,
                      const char* code) {
    for (const auto& message : messages) {
        if (message.code.value == code) return true;
    }
    return false;
}

bool expectation_has_code(const tools::FixtureExpectation& expectation,
                          const char* code) {
    for (const auto& expected_code : expectation.expected_report_codes) {
        if (expected_code == code) return true;
    }
    return false;
}

bool has_redundancy_code(const diagnostics::DiagnosticOutput& output,
                         const char* code) {
    for (const auto& set : output.redundancy_sets) {
        if (set.code == code) return true;
    }
    return false;
}

}  // namespace

TEST(ContractToolsContract, FixtureGenerationIsSeedDeterministic) {
    auto first = tools::build_fixture(
        tools::FixtureBuildRequest{tools::FixtureKind::two_component_distance, 123});
    auto second = tools::build_fixture(
        tools::FixtureBuildRequest{tools::FixtureKind::two_component_distance, 123});

    EXPECT_EQ(first.payload.provenance.fixture_id, second.payload.provenance.fixture_id);
    EXPECT_EQ(first.payload.provenance.deterministic_seed,
              second.payload.provenance.deterministic_seed);
    EXPECT_EQ(first.payload.model.entities.size(), second.payload.model.entities.size());
    EXPECT_EQ(first.payload.model.constraints.size(), second.payload.model.constraints.size());
}

TEST(ContractToolsContract, GeneratedFixturePassesKernelValidation) {
    auto fixture = tools::build_fixture(
        tools::FixtureBuildRequest{tools::FixtureKind::two_point_distance, 0});

    auto invariants = tools::check_invariants(
        tools::InvariantCheckRequest{fixture.payload.model, fixture.payload.whole_context});

    EXPECT_TRUE(invariants.payload.valid);
    EXPECT_EQ(invariants.payload.entity_count, 2);
    EXPECT_EQ(invariants.payload.constraint_count, 1);
    EXPECT_TRUE(invariants.payload.messages.empty());
}

TEST(ContractToolsContract, InvariantReportNamesFailures) {
    auto fixture = tools::build_fixture(
        tools::FixtureBuildRequest{tools::FixtureKind::missing_entity_reference, 0});

    auto invariants = tools::check_invariants(
        tools::InvariantCheckRequest{fixture.payload.model, fixture.payload.whole_context});

    EXPECT_FALSE(invariants.payload.valid);
    EXPECT_TRUE(has_message_code(invariants.payload.messages, "kernel.missing_entity"));
    EXPECT_EQ(invariants.report.status, kernel::StageStatus::error);
}

TEST(ContractToolsContract, GoldenReportDigestIsStable) {
    auto fixture = tools::build_fixture(
        tools::FixtureBuildRequest{tools::FixtureKind::two_point_distance, 17});

    auto first = tools::write_golden_report(
        tools::GoldenReportRequest{fixture.payload, "two_point"});
    auto second = tools::write_golden_report(
        tools::GoldenReportRequest{fixture.payload, "two_point"});

    EXPECT_EQ(first.payload.digest_algorithm, "fnv1a64");
    EXPECT_EQ(first.payload.digest, second.payload.digest);
    EXPECT_EQ(first.payload.canonical_summary, second.payload.canonical_summary);
    EXPECT_FALSE(first.payload.digest.empty());
}

TEST(ContractToolsContract, CorpusGenerationIncludesStructuredNegativeFixtures) {
    auto corpus = tools::generate_corpus(
        tools::CorpusGenerationRequest{{}, 700, true});

    EXPECT_EQ(corpus.payload.fixtures.size(), 10U);
    EXPECT_EQ(corpus.payload.golden_report.report_name, "fixture_corpus");
    EXPECT_FALSE(corpus.payload.golden_report.digest.empty());

    const std::string& summary = corpus.payload.golden_report.canonical_summary;
    EXPECT_NE(summary.find("missing_entity_reference|invalid|"), std::string::npos);
    EXPECT_NE(summary.find("inconsistent_distance_pair|inconsistent|"),
              std::string::npos);
    EXPECT_NE(summary.find("singular_coincident_points|singular|"),
              std::string::npos);
    EXPECT_NE(summary.find("gluing.boundary_projection_mismatch"),
              std::string::npos);
}

TEST(ContractToolsContract, GoldenReportNamesFixtureExpectations) {
    auto fixture = tools::build_fixture(
        tools::FixtureBuildRequest{tools::FixtureKind::inconsistent_distance_pair, 17});

    auto report = tools::write_golden_report(
        tools::GoldenReportRequest{fixture.payload, "inconsistent_pair"});

    EXPECT_NE(report.payload.canonical_summary.find(
                  "inconsistent_distance_pair|inconsistent|"),
              std::string::npos);
    EXPECT_NE(report.payload.canonical_summary.find("Inconsistent"),
              std::string::npos);
    EXPECT_NE(report.payload.canonical_summary.find("diagnostics.residual_conflict"),
              std::string::npos);
}

TEST(ContractToolsContract, NegativeFixtureExpectationsMatchKernelEvidence) {
    auto fixture = tools::build_fixture(
        tools::FixtureBuildRequest{tools::FixtureKind::missing_entity_reference, 5});

    auto invariants = tools::check_invariants(
        tools::InvariantCheckRequest{fixture.payload.model, fixture.payload.whole_context});

    EXPECT_FALSE(invariants.payload.valid);
    EXPECT_EQ(fixture.payload.expectation.expected_status,
              kernel::SolveStatus::invalid_model);
    EXPECT_TRUE(expectation_has_code(fixture.payload.expectation, "kernel.missing_entity"));
    EXPECT_TRUE(has_message_code(invariants.payload.messages, "kernel.missing_entity"));
}

TEST(ContractToolsContract, OverConstrainedFixtureProducesRedundancyEvidence) {
    auto fixture = tools::build_fixture(
        tools::FixtureBuildRequest{
            tools::FixtureKind::over_constrained_duplicate_distance, 9});
    auto task = numeric::make_numeric_task(
        fixture.payload.model,
        fixture.payload.whole_context,
        fixture.payload.whole_context.entity_ids,
        fixture.payload.whole_context.constraint_ids,
        kernel::GaugePolicy{});
    auto numeric_report = numeric::solve_local(task);

    diagnostics::DiagnosticInput input;
    input.phase = diagnostics::DiagnosticPhase::post_local_solve;
    input.model = fixture.payload.model;
    input.context = fixture.payload.whole_context;
    input.numeric_report = numeric_report;
    auto output = diagnostics::diagnose(input);

    EXPECT_TRUE(expectation_has_code(
        fixture.payload.expectation,
        "diagnostics.overconstrained_redundancy_candidate"));
    EXPECT_TRUE(has_redundancy_code(
        output,
        "diagnostics.overconstrained_redundancy_candidate"));
}
