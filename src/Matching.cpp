#include "fhi/Matching.hpp"

#include <algorithm>
#include <limits>
#include <queue>
#include <stdexcept>
#include <unordered_set>

namespace fhi {
namespace {

constexpr int unmatched = -1;
constexpr int infinity_distance = std::numeric_limits<int>::max();

} // namespace

void Matching::add_edge(VertexId h_node, VertexId g_node) {
    add_h_node(h_node);
    add_g_node(g_node);
    insert_sorted_unique(h_to_g_[h_node], g_node);
}

void Matching::remove_edge(VertexId h_node, VertexId g_node) {
    auto it = h_to_g_.find(h_node);
    if (it == h_to_g_.end()) {
        return;
    }
    erase_value(it->second, g_node);
}

void Matching::add_h_node(VertexId h_node) {
    insert_sorted_unique(h_nodes_, h_node);
    h_to_g_.try_emplace(h_node, VertexList{});
}

void Matching::add_g_node(VertexId g_node) {
    insert_sorted_unique(g_nodes_, g_node);
}

bool Matching::has_h_node(VertexId h_node) const {
    return std::binary_search(h_nodes_.begin(), h_nodes_.end(), h_node);
}

bool Matching::linked(VertexId h_node, VertexId g_node) const {
    const auto it = h_to_g_.find(h_node);
    if (it == h_to_g_.end()) {
        return false;
    }
    return std::binary_search(it->second.begin(), it->second.end(), g_node);
}

VertexList Matching::h_node_neighbors(VertexId h_node) const {
    const auto it = h_to_g_.find(h_node);
    if (it == h_to_g_.end()) {
        return {};
    }
    return it->second;
}

VertexList Matching::g_node_neighbors(VertexId g_node) const {
    VertexList neighbors;
    for (const auto h_node : h_nodes_) {
        if (linked(h_node, g_node)) {
            neighbors.push_back(h_node);
        }
    }
    return neighbors;
}

bool Matching::match_exists() const {
    return match().has_value();
}

std::optional<std::unordered_map<VertexId, VertexId>> Matching::match() const {
    if (h_nodes_.empty()) {
        return std::unordered_map<VertexId, VertexId>{};
    }

    std::unordered_map<VertexId, int> h_index;
    std::unordered_map<VertexId, int> g_index;
    for (int i = 0; i < static_cast<int>(h_nodes_.size()); ++i) {
        h_index[h_nodes_[static_cast<std::size_t>(i)]] = i;
    }
    for (int i = 0; i < static_cast<int>(g_nodes_.size()); ++i) {
        g_index[g_nodes_[static_cast<std::size_t>(i)]] = i;
    }

    std::vector<std::vector<int>> adjacency(h_nodes_.size());
    for (std::size_t i = 0; i < h_nodes_.size(); ++i) {
        const auto it = h_to_g_.find(h_nodes_[i]);
        if (it == h_to_g_.end()) {
            return std::nullopt;
        }
        for (const auto g_node : it->second) {
            adjacency[i].push_back(g_index.at(g_node));
        }
        if (adjacency[i].empty()) {
            return std::nullopt;
        }
    }

    std::vector<int> pair_h(h_nodes_.size(), unmatched);
    std::vector<int> pair_g(g_nodes_.size(), unmatched);
    std::vector<int> distance(h_nodes_.size(), infinity_distance);

    auto bfs = [&]() {
        std::queue<int> queue;
        bool found_free_g = false;
        for (int h = 0; h < static_cast<int>(h_nodes_.size()); ++h) {
            if (pair_h[static_cast<std::size_t>(h)] == unmatched) {
                distance[static_cast<std::size_t>(h)] = 0;
                queue.push(h);
            } else {
                distance[static_cast<std::size_t>(h)] = infinity_distance;
            }
        }

        while (!queue.empty()) {
            const auto h = queue.front();
            queue.pop();
            for (const auto g : adjacency[static_cast<std::size_t>(h)]) {
                const auto matched_h = pair_g[static_cast<std::size_t>(g)];
                if (matched_h == unmatched) {
                    found_free_g = true;
                } else if (distance[static_cast<std::size_t>(matched_h)] == infinity_distance) {
                    distance[static_cast<std::size_t>(matched_h)] = distance[static_cast<std::size_t>(h)] + 1;
                    queue.push(matched_h);
                }
            }
        }
        return found_free_g;
    };

    auto dfs_impl = [&](auto&& self, int h) -> bool {
        for (const auto g : adjacency[static_cast<std::size_t>(h)]) {
            const auto matched_h = pair_g[static_cast<std::size_t>(g)];
            if (matched_h == unmatched ||
                (distance[static_cast<std::size_t>(matched_h)] == distance[static_cast<std::size_t>(h)] + 1 && self(self, matched_h))) {
                pair_h[static_cast<std::size_t>(h)] = g;
                pair_g[static_cast<std::size_t>(g)] = h;
                return true;
            }
        }
        distance[static_cast<std::size_t>(h)] = infinity_distance;
        return false;
    };

    std::size_t matching_size = 0;
    while (bfs()) {
        for (int h = 0; h < static_cast<int>(h_nodes_.size()); ++h) {
            if (pair_h[static_cast<std::size_t>(h)] == unmatched && dfs_impl(dfs_impl, h)) {
                ++matching_size;
            }
        }
    }

    if (matching_size != h_nodes_.size()) {
        return std::nullopt;
    }

    std::unordered_map<VertexId, VertexId> result;
    for (std::size_t h = 0; h < h_nodes_.size(); ++h) {
        result[h_nodes_[h]] = g_nodes_[static_cast<std::size_t>(pair_h[h])];
    }
    return result;
}

void Matching::insert_sorted_unique(VertexList& values, VertexId value) {
    const auto it = std::lower_bound(values.begin(), values.end(), value);
    if (it == values.end() || *it != value) {
        values.insert(it, value);
    }
}

void Matching::erase_value(VertexList& values, VertexId value) {
    const auto it = std::lower_bound(values.begin(), values.end(), value);
    if (it != values.end() && *it == value) {
        values.erase(it);
    }
}

} // namespace fhi
