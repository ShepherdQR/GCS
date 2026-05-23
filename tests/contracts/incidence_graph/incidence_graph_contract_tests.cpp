import gcs.contract_tools;
import gcs.incidence_graph;
import gcs.kernel;

#include <gtest/gtest.h>

#include <string>

namespace {

namespace graph = gcs::graph;
namespace kernel = gcs::kernel;

bool has_code(const kernel::StageReport& report, const char* code) {
    for (const auto& message : report.messages) {
        if (message.code.value == code) return true;
    }
    return false;
}

}  // namespace

TEST(IncidenceGraphContract, BuildsHyperedgesForConstraints) {
    auto model = gcs::tools::make_two_point_distance_model();

    auto hypergraph = graph::build_hypergraph(graph::HypergraphBuildRequest{model, {}});

    EXPECT_EQ(hypergraph.report.status, kernel::StageStatus::ok);
    ASSERT_EQ(hypergraph.payload.hyperedges.size(), 1U);
    EXPECT_EQ(hypergraph.payload.hyperedges.front().id.value, 0U);
    EXPECT_EQ(hypergraph.payload.hyperedges.front().constraint_id.value, 0U);
    EXPECT_EQ(hypergraph.payload.hyperedges.front().entity_ids.size(), 2U);
    EXPECT_FALSE(hypergraph.payload.hyperedges.front().malformed);
}

TEST(IncidenceGraphContract, ReverseIndexNamesAllConstraintsPerEntity) {
    auto model = gcs::tools::make_two_component_distance_model();
    auto hypergraph = graph::build_hypergraph(graph::HypergraphBuildRequest{model, {}});

    auto indices = graph::build_indices(hypergraph.payload);

    ASSERT_EQ(indices.payload.entity_incidence.size(), 4U);
    EXPECT_EQ(indices.payload.entity_incidence[0].entity_id.value, 0U);
    ASSERT_EQ(indices.payload.entity_incidence[0].constraint_ids.size(), 1U);
    EXPECT_EQ(indices.payload.entity_incidence[0].constraint_ids.front().value, 0U);
    EXPECT_EQ(indices.payload.entity_incidence[2].entity_id.value, 2U);
    ASSERT_EQ(indices.payload.entity_incidence[2].constraint_ids.size(), 1U);
    EXPECT_EQ(indices.payload.entity_incidence[2].constraint_ids.front().value, 1U);
}

TEST(IncidenceGraphContract, ComponentsCoverEachEntityOnce) {
    auto model = gcs::tools::make_two_component_distance_model();
    auto indices = graph::build_incidence_indices(graph::IncidenceInput{model});

    ASSERT_EQ(indices.connected_components.size(), 2U);
    EXPECT_EQ(indices.connected_components[0].entity_ids.size(), 2U);
    EXPECT_EQ(indices.connected_components[1].entity_ids.size(), 2U);
    EXPECT_EQ(indices.connected_components[0].constraint_ids.size(), 1U);
    EXPECT_EQ(indices.connected_components[1].constraint_ids.size(), 1U);
    EXPECT_EQ(indices.connected_components[0].rigid_set_ids.size(), 2U);
    EXPECT_EQ(indices.connected_components[1].rigid_set_ids.size(), 2U);
}

TEST(IncidenceGraphContract, ReportsMissingEntityReferences) {
    auto model = gcs::tools::make_missing_entity_reference_model();

    auto hypergraph = graph::build_hypergraph(graph::HypergraphBuildRequest{model, {}});
    auto indices = graph::build_indices(hypergraph.payload);

    EXPECT_EQ(hypergraph.report.status, kernel::StageStatus::error);
    EXPECT_TRUE(has_code(hypergraph.report, "incidence.missing_entity"));
    ASSERT_EQ(hypergraph.payload.malformed_edges.size(), 1U);
    EXPECT_EQ(hypergraph.payload.malformed_edges.front().constraint_id.value, 7U);
    ASSERT_EQ(indices.payload.constraint_incidence.size(), 2U);
    EXPECT_FALSE(indices.payload.constraint_incidence.back().valid);
}

TEST(IncidenceGraphContract, RigidBodyProjectionIsDeterministic) {
    auto model = gcs::tools::make_two_component_distance_model();
    auto hypergraph = graph::build_hypergraph(graph::HypergraphBuildRequest{model, {}});

    auto first = graph::build_rigid_body_graph(model, hypergraph.payload);
    auto second = graph::build_rigid_body_graph(model, hypergraph.payload);

    ASSERT_EQ(first.payload.nodes.size(), 4U);
    ASSERT_EQ(first.payload.edges.size(), 2U);
    EXPECT_EQ(first.payload.edges[0].first_rigid_set_id.value, 0U);
    EXPECT_EQ(first.payload.edges[0].second_rigid_set_id.value, 1U);
    EXPECT_EQ(first.payload.edges[1].first_rigid_set_id.value, 2U);
    EXPECT_EQ(first.payload.edges[1].second_rigid_set_id.value, 3U);
    EXPECT_EQ(first.payload.edges[0].constraint_ids.front().value,
              second.payload.edges[0].constraint_ids.front().value);
}

TEST(IncidenceGraphContract, GraphDumpIsCanonical) {
    auto model = gcs::tools::make_missing_entity_reference_model();
    auto hypergraph = graph::build_hypergraph(graph::HypergraphBuildRequest{model, {}});

    auto first = graph::dump_graph(hypergraph.payload);
    auto second = graph::dump_graph(hypergraph.payload);

    EXPECT_EQ(first.payload.canonical_text, second.payload.canonical_text);
    EXPECT_EQ(first.payload.hyperedge_count, 2);
    EXPECT_EQ(first.payload.malformed_edge_count, 1);
    EXPECT_NE(first.payload.canonical_text.find("c=7 missing=999"),
              std::string::npos);
}
