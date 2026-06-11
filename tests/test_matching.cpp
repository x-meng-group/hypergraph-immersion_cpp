#include "Test.hpp"

#include "fhi/Matching.hpp"

namespace {

void test_matching_exists() {
    fhi::Matching matching;
    matching.add_edge(0, 10);
    matching.add_edge(0, 11);
    matching.add_edge(1, 11);
    FHI_REQUIRE(matching.match_exists());
    const auto result = matching.match();
    FHI_REQUIRE(result.has_value());
    FHI_REQUIRE(result->size() == 2);
    FHI_REQUIRE(result->at(0) != result->at(1));
}

void test_matching_failure() {
    fhi::Matching matching;
    matching.add_h_node(0);
    matching.add_h_node(1);
    matching.add_edge(0, 10);
    FHI_REQUIRE(!matching.match_exists());
}

} // namespace

void run_matching_tests() {
    test_matching_exists();
    test_matching_failure();
}
