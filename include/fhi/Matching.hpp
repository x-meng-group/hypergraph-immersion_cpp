#pragma once

#include "fhi/Types.hpp"

#include <optional>
#include <unordered_map>
#include <vector>

namespace fhi {

class Matching {
public:
    void add_edge(VertexId h_node, VertexId g_node);
    void remove_edge(VertexId h_node, VertexId g_node);
    void add_h_node(VertexId h_node);
    void add_g_node(VertexId g_node);

    [[nodiscard]] bool has_h_node(VertexId h_node) const;
    [[nodiscard]] bool linked(VertexId h_node, VertexId g_node) const;
    [[nodiscard]] VertexList h_node_neighbors(VertexId h_node) const;
    [[nodiscard]] VertexList g_node_neighbors(VertexId g_node) const;
    [[nodiscard]] bool match_exists() const;
    [[nodiscard]] std::optional<std::unordered_map<VertexId, VertexId>> match() const;

private:
    VertexList h_nodes_;
    VertexList g_nodes_;
    std::unordered_map<VertexId, VertexList> h_to_g_;

    static void insert_sorted_unique(VertexList& values, VertexId value);
    static void erase_value(VertexList& values, VertexId value);
};

} // namespace fhi
