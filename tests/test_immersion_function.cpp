#include "Test.hpp"

#include "fhi/ImmersionFunction.hpp"

#include <unordered_map>

void run_hypergraph_tests();
void run_matching_tests();
void run_quick_immersion_tests();

namespace {

void test_identity_immersion() {
    const fhi::Hypergraph g({{0, 1}, {1, 2}});
    const fhi::Hypergraph h({{0, 1}, {1, 2}});
    fhi::ImmersionFunction immersion(
        {{0, 0}, {1, 1}, {2, 2}},
        {{0}, {1}},
        g,
        h);
    FHI_REQUIRE(immersion.is_immersion());
    FHI_REQUIRE(immersion.is_reasonable());
    FHI_REQUIRE(immersion.cost() == 2);
}

void test_rejects_reused_g_edge() {
    const fhi::Hypergraph g({{0, 1}, {1, 2}});
    const fhi::Hypergraph h({{0, 1}, {1, 2}});
    fhi::ImmersionFunction immersion(
        {{0, 0}, {1, 1}, {2, 2}},
        {{0}, {0}},
        g,
        h);
    FHI_REQUIRE(!immersion.is_immersion());
}

} // namespace

int main() {
    run_hypergraph_tests();
    run_matching_tests();
    test_identity_immersion();
    test_rejects_reused_g_edge();
    run_quick_immersion_tests();
    return 0;
}
