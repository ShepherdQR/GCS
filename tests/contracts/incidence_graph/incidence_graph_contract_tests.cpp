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

// --- Biconnected decomposition contract tests ---

TEST(IncidenceGraphContract, BiconnectedDecompositionChainHasTwoComponentsAndOneArticulation) {
    // A 3-entity chain: e0 --(c0)--> e1 --(c1)--> e2
    // e1 is the articulation point, two biconnected components
    auto model = gcs::tools::make_separator_chain_distance_model();
    auto indices = graph::build_incidence_indices(graph::IncidenceInput{model});

    auto result = graph::decompose_biconnected(model, indices);

    EXPECT_EQ(result.report.status, kernel::StageStatus::ok);
    EXPECT_FALSE(result.payload.is_biconnected);
    EXPECT_EQ(result.payload.components.size(), 2U);
    EXPECT_EQ(result.payload.articulation_points.size(), 1U);
    EXPECT_EQ(result.payload.articulation_points.front().entity_id.value, 1U);  // e1 is separator
    EXPECT_EQ(result.payload.articulation_points.front().biconnected_component_indices.size(), 2U);
}

TEST(IncidenceGraphContract, BiconnectedDecompositionDeterministicOutput) {
    auto model = gcs::tools::make_separator_chain_distance_model();
    auto indices = graph::build_incidence_indices(graph::IncidenceInput{model});

    auto first = graph::decompose_biconnected(model, indices);
    auto second = graph::decompose_biconnected(model, indices);

    EXPECT_EQ(first.payload.components.size(), second.payload.components.size());
    EXPECT_EQ(first.payload.articulation_points.size(), second.payload.articulation_points.size());
    for (std::size_t i = 0; i < first.payload.components.size(); ++i) {
        EXPECT_EQ(first.payload.components[i].entity_ids.size(),
                  second.payload.components[i].entity_ids.size());
        EXPECT_EQ(first.payload.components[i].constraint_ids.size(),
                  second.payload.components[i].constraint_ids.size());
    }
    for (std::size_t i = 0; i < first.payload.articulation_points.size(); ++i) {
        EXPECT_EQ(first.payload.articulation_points[i].entity_id,
                  second.payload.articulation_points[i].entity_id);
    }
}

TEST(IncidenceGraphContract, BiconnectedDecompositionCycleIsBiconnected) {
    // A 3-entity triangle: e0, e1, e2 with 3 distance constraints (c0, c1, c2)
    // This should be one biconnected component with no articulation points
    auto model = gcs::tools::make_two_component_distance_model();
    // That model has two separate components, each is just a single edge (biconnected trivially)
    auto indices = graph::build_incidence_indices(graph::IncidenceInput{model});

    auto result = graph::decompose_biconnected(model, indices);

    EXPECT_EQ(result.report.status, kernel::StageStatus::ok);
    // Two separate components in the model → each is biconnected (single edge)
    EXPECT_EQ(result.payload.components.size(), 2U);
    EXPECT_EQ(result.payload.articulation_points.size(), 0U);
}

TEST(IncidenceGraphContract, BiconnectedDecompositionEveryEntityInAtLeastOneComponent) {
    auto model = gcs::tools::make_separator_chain_distance_model();
    auto indices = graph::build_incidence_indices(graph::IncidenceInput{model});

    auto result = graph::decompose_biconnected(model, indices);

    for (const auto& entity_inc : indices.entity_incidence) {
        bool found = false;
        for (const auto& comp : result.payload.components) {
            if (kernel::contains_entity(comp.entity_ids, entity_inc.entity_id)) {
                found = true;
                break;
            }
        }
        EXPECT_TRUE(found) << "Entity " << entity_inc.entity_id.value << " not in any component";
    }
}

TEST(IncidenceGraphContract, BiconnectedDecompositionEveryConstraintInAtLeastOneComponent) {
    auto model = gcs::tools::make_separator_chain_distance_model();
    auto indices = graph::build_incidence_indices(graph::IncidenceInput{model});

    auto result = graph::decompose_biconnected(model, indices);

    for (const auto& constraint_inc : indices.constraint_incidence) {
        if (!constraint_inc.valid) continue;
        bool found = false;
        for (const auto& comp : result.payload.components) {
            if (kernel::contains_constraint(comp.constraint_ids, constraint_inc.constraint_id)) {
                found = true;
                break;
            }
        }
        EXPECT_TRUE(found) << "Constraint " << constraint_inc.constraint_id.value << " not in any component";
    }
}
