#pragma once

#include "fhi/Types.hpp"

#include <iosfwd>
#include <string>
#include <unordered_map>
#include <vector>

namespace fhi {

class Hypergraph {
public:
    Hypergraph() = default;
    explicit Hypergraph(std::vector<VertexList> edges);

    static Hypergraph from_encoded_string(const std::string& encoded);

    [[nodiscard]] std::string to_encoded_string(bool sort_edges = false) const;

    [[nodiscard]] std::size_t vertex_count() const noexcept { return incident_edges_.size(); }
    [[nodiscard]] std::size_t edge_count() const noexcept { return edges_.size(); }

    [[nodiscard]] const VertexList& edge_vertices(EdgeId edge) const;
    [[nodiscard]] const EdgeList& incident_edges(VertexId vertex) const;
    [[nodiscard]] const EdgeList& adjacent_edges(EdgeId edge) const;

    [[nodiscard]] const std::vector<VertexList>& edges() const noexcept { return edges_; }
    [[nodiscard]] VertexList vertices_of_edges(const EdgeList& edge_ids) const;
    [[nodiscard]] bool is_connected(const EdgeList& edge_ids) const;
    [[nodiscard]] EdgeId largest_edge(const EdgeList& edge_ids) const;
    [[nodiscard]] std::vector<EdgeList> clusters(const EdgeList& edge_ids) const;

    [[nodiscard]] bool operator==(const Hypergraph& other) const noexcept;
    [[nodiscard]] bool operator!=(const Hypergraph& other) const noexcept { return !(*this == other); }

private:
    std::vector<VertexList> edges_;
    std::vector<EdgeList> incident_edges_;
    std::vector<EdgeList> edge_adjacency_;

    void normalize_edges();
    void rebuild_indexes();
    void validate_edge(EdgeId edge) const;
    void validate_vertex(VertexId vertex) const;
};

std::ostream& operator<<(std::ostream& os, const Hypergraph& hypergraph);

} // namespace fhi
