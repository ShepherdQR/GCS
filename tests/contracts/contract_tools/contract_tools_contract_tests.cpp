import gcs.contract_tools;
import gcs.kernel;

#include <gtest/gtest.h>

#include <vector>

namespace {

namespace kernel = gcs::kernel;
namespace tools = gcs::tools;

bool has_message_code(const std::vector<kernel::ReportMessage>& messages,
                      const char* code) {
    for (const auto& message : messages) {
        if (message.code.value == code) return true;
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
