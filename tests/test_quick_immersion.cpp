#include "Test.hpp"

#include "fhi/QuickImmersion.hpp"

namespace {

void test_identity_immersion_succeeds() {
    const fhi::Hypergraph graph({{0, 1}, {1, 2}});
    fhi::QuickImmersion solver(graph, graph);
    FHI_REQUIRE(solver.execute());
    FHI_REQUIRE(!solver.immersions().empty());
    FHI_REQUIRE(solver.immersions().front().is_immersion());
}

void test_extra_target_edge_succeeds() {
    const fhi::Hypergraph h({{0, 1}, {1, 2}});
    const fhi::Hypergraph g({{0, 1}, {1, 2}, {2, 3}});
    fhi::QuickImmersion solver(g, h);
    FHI_REQUIRE(solver.execute());
    FHI_REQUIRE(solver.immersions().front().is_immersion());
}

void test_too_small_target_fails() {
    const fhi::Hypergraph h({{0, 1}, {1, 2}});
    const fhi::Hypergraph g({{0, 1}});
    fhi::QuickImmersion solver(g, h);
    FHI_REQUIRE(!solver.execute());
}

void test_disconnected_target_fails_for_connected_pattern() {
    const fhi::Hypergraph h({{0, 1}, {1, 2}});
    const fhi::Hypergraph g({{0, 1}, {2, 3}});
    fhi::QuickImmersion solver(g, h);
    FHI_REQUIRE(!solver.execute());
}

std::vector<fhi::Hypergraph> small_hypergraphs() {
    std::vector<fhi::Hypergraph> graphs;
    const std::vector<fhi::VertexList> edge_pool{
        {0, 1},
        {0, 2},
        {1, 2},
        {0, 1, 2},
    };

    for (std::size_t i = 0; i < edge_pool.size(); ++i) {
        graphs.emplace_back(std::vector<fhi::VertexList>{edge_pool[i]});
    }
    for (std::size_t i = 0; i < edge_pool.size(); ++i) {
        for (std::size_t j = i + 1; j < edge_pool.size(); ++j) {
            fhi::Hypergraph graph({edge_pool[i], edge_pool[j]});
            if (graph.is_connected({0, 1})) {
                graphs.push_back(graph);
            }
        }
    }
    return graphs;
}

void test_small_self_immersions() {
    for (const auto& graph : small_hypergraphs()) {
        fhi::QuickImmersion solver(graph, graph);
        FHI_REQUIRE(solver.execute());
        FHI_REQUIRE(!solver.immersions().empty());
        FHI_REQUIRE(solver.immersions().front().is_immersion());
    }
}

void test_single_edge_pattern_when_target_has_large_edge() {
    const fhi::Hypergraph h({{0, 1}});
    const fhi::Hypergraph g({{0, 1, 2}, {2, 3}});
    fhi::QuickImmersion solver(g, h);
    FHI_REQUIRE(solver.execute());
    FHI_REQUIRE(solver.immersions().front().is_immersion());
}

void test_disconnected_pattern_self_immersion_succeeds() {
    const fhi::Hypergraph graph({{0, 1}, {2, 3}});
    fhi::QuickImmersion solver(graph, graph);
    FHI_REQUIRE(solver.execute());
    FHI_REQUIRE(!solver.immersions().empty());
    FHI_REQUIRE(solver.immersions().front().is_immersion());
}

void test_disconnected_pattern_into_disconnected_target_succeeds() {
    const fhi::Hypergraph h({{0, 1}, {2, 3}});
    const fhi::Hypergraph g({{0, 1}, {2, 3}, {4, 5}});
    fhi::QuickImmersion solver(g, h);
    FHI_REQUIRE(solver.execute());
    FHI_REQUIRE(solver.immersions().front().is_immersion());
}

void test_disconnected_pattern_components_can_share_target_component() {
    const fhi::Hypergraph h({{0, 1}, {2, 3}});
    const fhi::Hypergraph g({{0, 1}, {2, 3}, {1, 2}});
    fhi::QuickImmersion solver(g, h);
    FHI_REQUIRE(solver.execute());
    FHI_REQUIRE(solver.immersions().front().is_immersion());
}

void test_later_disconnected_component_can_expand_in_target() {
    const fhi::Hypergraph h({{0, 1, 2, 3}, {4, 5, 6}});
    const fhi::Hypergraph g({{0, 1, 2, 3}, {4, 5}, {5, 6}});
    fhi::QuickImmersion solver(g, h);
    FHI_REQUIRE(solver.execute());
    FHI_REQUIRE(solver.immersions().front().is_immersion());
}

void test_three_disconnected_pattern_components_succeed() {
    const fhi::Hypergraph graph({{0, 1}, {2, 3}, {4, 5}});
    fhi::QuickImmersion solver(graph, graph);
    FHI_REQUIRE(solver.execute());
    FHI_REQUIRE(solver.immersions().front().is_immersion());
}

void test_random_priority_disconnected_pattern_succeeds() {
    const fhi::Hypergraph h({{0, 1}, {2, 3}, {4, 5}});
    const fhi::Hypergraph g({{0, 1}, {2, 3}, {4, 5}, {5, 6}});
    fhi::QuickImmersionOptions options;
    options.use_random_priority = true;
    fhi::QuickImmersion solver(g, h, options);
    FHI_REQUIRE(solver.execute());
    FHI_REQUIRE(solver.immersions().front().is_immersion());
}

void test_disconnected_pattern_respects_zero_max_depth() {
    const fhi::Hypergraph h({{0, 1, 2}, {3, 4}});
    const fhi::Hypergraph g({{0, 1}, {1, 2}, {3, 4}});
    fhi::QuickImmersionOptions options;
    options.max_depth = 0;
    fhi::QuickImmersion solver(g, h, options);
    FHI_REQUIRE(!solver.execute());
}

void test_disconnected_pattern_needs_enough_distinct_target_vertices() {
    const fhi::Hypergraph h({{0, 1}, {2, 3}});
    const fhi::Hypergraph g({{0, 1}, {1, 2}});
    fhi::QuickImmersion solver(g, h);
    FHI_REQUIRE(!solver.execute());
}

void test_disconnected_target_cannot_cover_large_component_without_path() {
    const fhi::Hypergraph h({{0, 1, 2}, {3, 4}});
    const fhi::Hypergraph g({{0, 1}, {2, 3}, {4, 5}});
    fhi::QuickImmersion solver(g, h);
    FHI_REQUIRE(!solver.execute());
}

} // namespace

void run_quick_immersion_tests() {
    test_identity_immersion_succeeds();
    test_extra_target_edge_succeeds();
    test_too_small_target_fails();
    test_disconnected_target_fails_for_connected_pattern();
    test_small_self_immersions();
    test_single_edge_pattern_when_target_has_large_edge();
    test_disconnected_pattern_self_immersion_succeeds();
    test_disconnected_pattern_into_disconnected_target_succeeds();
    test_disconnected_pattern_components_can_share_target_component();
    test_later_disconnected_component_can_expand_in_target();
    test_three_disconnected_pattern_components_succeed();
    test_random_priority_disconnected_pattern_succeeds();
    test_disconnected_pattern_respects_zero_max_depth();
    test_disconnected_pattern_needs_enough_distinct_target_vertices();
    test_disconnected_target_cannot_cover_large_component_without_path();
}
