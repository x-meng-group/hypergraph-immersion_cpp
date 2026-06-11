#include "Test.hpp"

#include "fhi/Hypergraph.hpp"

namespace {

void test_basic_indexes() {
    const fhi::Hypergraph graph({{0, 1}, {1, 2}, {3}});
    FHI_REQUIRE(graph.vertex_count() == 4);
    FHI_REQUIRE(graph.edge_count() == 3);
    FHI_REQUIRE((graph.incident_edges(1) == fhi::EdgeList{0, 1}));
    FHI_REQUIRE((graph.adjacent_edges(0) == fhi::EdgeList{1}));
    FHI_REQUIRE(graph.is_connected({0, 1}));
    FHI_REQUIRE(!graph.is_connected({0, 2}));
    FHI_REQUIRE((graph.vertices_of_edges({0, 1}) == fhi::VertexList{0, 1, 2}));
}

void test_encoded_roundtrip() {
    const fhi::Hypergraph graph({{0, 1}, {1, 2, 3}});
    const auto encoded = graph.to_encoded_string(true);
    const auto decoded = fhi::Hypergraph::from_encoded_string(encoded);
    FHI_REQUIRE(decoded == graph);
}

} // namespace

void run_hypergraph_tests() {
    test_basic_indexes();
    test_encoded_roundtrip();
}
