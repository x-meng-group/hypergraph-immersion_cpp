#include "fhi/ImmersionFunction.hpp"

#include <algorithm>
#include <stdexcept>
#include <unordered_set>

namespace fhi {
namespace {

template <class T>
bool contains_unique(const std::vector<T>& values, T value) {
    return std::binary_search(values.begin(), values.end(), value);
}

} // namespace

ImmersionFunction::ImmersionFunction(
    std::unordered_map<VertexId, VertexId> node_mapping,
    std::vector<EdgeList> edge_mapping,
    Hypergraph g,
    Hypergraph h)
    : node_mapping_(std::move(node_mapping)),
      edge_mapping_(std::move(edge_mapping)),
      g_(std::move(g)),
      h_(std::move(h)) {
    for (auto& edge_image : edge_mapping_) {
        std::sort(edge_image.begin(), edge_image.end());
        edge_image.erase(std::unique(edge_image.begin(), edge_image.end()), edge_image.end());
    }
}

VertexId ImmersionFunction::evaluate_node(VertexId h_node) const {
    const auto it = node_mapping_.find(h_node);
    if (it == node_mapping_.end()) {
        throw std::out_of_range("H node is not present in this immersion function");
    }
    return it->second;
}

const EdgeList& ImmersionFunction::evaluate_edge(EdgeId h_edge) const {
    if (h_edge < 0 || static_cast<std::size_t>(h_edge) >= edge_mapping_.size()) {
        throw std::out_of_range("H edge is not present in this immersion function");
    }
    return edge_mapping_[static_cast<std::size_t>(h_edge)];
}

bool ImmersionFunction::is_immersion() const {
    if (node_mapping_.size() != h_.vertex_count() || edge_mapping_.size() != h_.edge_count()) {
        return false;
    }

    std::unordered_set<VertexId> mapped_g_vertices;
    for (VertexId h_vertex = 0; h_vertex < static_cast<VertexId>(h_.vertex_count()); ++h_vertex) {
        const auto it = node_mapping_.find(h_vertex);
        if (it == node_mapping_.end()) {
            return false;
        }
        const auto g_vertex = it->second;
        if (g_vertex < 0 || static_cast<std::size_t>(g_vertex) >= g_.vertex_count()) {
            return false;
        }
        if (!mapped_g_vertices.insert(g_vertex).second) {
            return false;
        }
    }

    std::unordered_set<EdgeId> used_g_edges;
    for (EdgeId h_edge = 0; h_edge < static_cast<EdgeId>(h_.edge_count()); ++h_edge) {
        const auto& g_edge_image = evaluate_edge(h_edge);
        if (g_edge_image.empty() || !g_.is_connected(g_edge_image)) {
            return false;
        }

        for (const auto g_edge : g_edge_image) {
            if (g_edge < 0 || static_cast<std::size_t>(g_edge) >= g_.edge_count()) {
                return false;
            }
            if (!used_g_edges.insert(g_edge).second) {
                return false;
            }
        }

        const auto image_vertices = g_.vertices_of_edges(g_edge_image);
        for (const auto h_vertex : h_.edge_vertices(h_edge)) {
            if (!contains_unique(image_vertices, evaluate_node(h_vertex))) {
                return false;
            }
        }
    }

    return true;
}

bool ImmersionFunction::is_reasonable() const {
    for (EdgeId h_edge = 0; h_edge < static_cast<EdgeId>(h_.edge_count()); ++h_edge) {
        const auto& g_edges = evaluate_edge(h_edge);
        for (const auto removed_edge : g_edges) {
            EdgeList reduced;
            reduced.reserve(g_edges.size() - 1);
            for (const auto g_edge : g_edges) {
                if (g_edge != removed_edge) {
                    reduced.push_back(g_edge);
                }
            }
            if (!reduced.empty() && g_.is_connected(reduced)) {
                const auto reduced_vertices = g_.vertices_of_edges(reduced);
                bool all_h_vertices_still_covered = true;
                for (const auto h_vertex : h_.edge_vertices(h_edge)) {
                    if (!contains_unique(reduced_vertices, evaluate_node(h_vertex))) {
                        all_h_vertices_still_covered = false;
                        break;
                    }
                }
                if (all_h_vertices_still_covered) {
                    return false;
                }
            }
        }
    }
    return true;
}

std::size_t ImmersionFunction::cost() const {
    std::size_t total = 0;
    for (const auto& edge_image : edge_mapping_) {
        total += edge_image.size();
    }
    return total;
}

} // namespace fhi
