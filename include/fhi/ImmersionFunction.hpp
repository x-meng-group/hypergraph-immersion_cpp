#pragma once

#include "fhi/Hypergraph.hpp"

#include <unordered_map>

namespace fhi {

class ImmersionFunction {
public:
    ImmersionFunction(
        std::unordered_map<VertexId, VertexId> node_mapping,
        std::vector<EdgeList> edge_mapping,
        Hypergraph g,
        Hypergraph h);

    [[nodiscard]] VertexId evaluate_node(VertexId h_node) const;
    [[nodiscard]] const EdgeList& evaluate_edge(EdgeId h_edge) const;
    [[nodiscard]] bool is_immersion() const;
    [[nodiscard]] bool is_reasonable() const;
    [[nodiscard]] std::size_t cost() const;

    [[nodiscard]] const Hypergraph& g() const noexcept { return g_; }
    [[nodiscard]] const Hypergraph& h() const noexcept { return h_; }
    [[nodiscard]] const std::unordered_map<VertexId, VertexId>& node_mapping() const noexcept { return node_mapping_; }
    [[nodiscard]] const std::vector<EdgeList>& edge_mapping() const noexcept { return edge_mapping_; }

private:
    std::unordered_map<VertexId, VertexId> node_mapping_;
    std::vector<EdgeList> edge_mapping_;
    Hypergraph g_;
    Hypergraph h_;
};

} // namespace fhi
