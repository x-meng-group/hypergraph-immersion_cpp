#include "fhi/QuickImmersion.hpp"

#include <algorithm>
#include <stdexcept>

namespace fhi {
namespace {

template <class T>
void normalize(std::vector<T>& values) {
    std::sort(values.begin(), values.end());
    values.erase(std::unique(values.begin(), values.end()), values.end());
}

template <class T>
void insert_unique(std::vector<T>& values, T value) {
    const auto it = std::lower_bound(values.begin(), values.end(), value);
    if (it == values.end() || *it != value) {
        values.insert(it, value);
    }
}

template <class T>
void erase_value(std::vector<T>& values, T value) {
    const auto it = std::lower_bound(values.begin(), values.end(), value);
    if (it != values.end() && *it == value) {
        values.erase(it);
    }
}

template <class T>
bool contains(const std::vector<T>& values, T value) {
    return std::binary_search(values.begin(), values.end(), value);
}

template <class T>
std::vector<T> set_union_vec(const std::vector<T>& lhs, const std::vector<T>& rhs) {
    std::vector<T> result;
    std::set_union(lhs.begin(), lhs.end(), rhs.begin(), rhs.end(), std::back_inserter(result));
    return result;
}

template <class T>
std::vector<T> set_intersection_vec(const std::vector<T>& lhs, const std::vector<T>& rhs) {
    std::vector<T> result;
    std::set_intersection(lhs.begin(), lhs.end(), rhs.begin(), rhs.end(), std::back_inserter(result));
    return result;
}

template <class T>
std::vector<T> set_difference_vec(const std::vector<T>& lhs, const std::vector<T>& rhs) {
    std::vector<T> result;
    std::set_difference(lhs.begin(), lhs.end(), rhs.begin(), rhs.end(), std::back_inserter(result));
    return result;
}

EdgeList all_edges(const Hypergraph& graph) {
    EdgeList edges;
    edges.reserve(graph.edge_count());
    for (EdgeId edge = 0; edge < static_cast<EdgeId>(graph.edge_count()); ++edge) {
        edges.push_back(edge);
    }
    return edges;
}

VertexList all_vertices(const Hypergraph& graph) {
    VertexList vertices;
    vertices.reserve(graph.vertex_count());
    for (VertexId vertex = 0; vertex < static_cast<VertexId>(graph.vertex_count()); ++vertex) {
        vertices.push_back(vertex);
    }
    return vertices;
}

} // namespace

QuickImmersion::QuickImmersion(Hypergraph g, Hypergraph h, QuickImmersionOptions options)
    : smart_depth_(options.dynamic_depth),
      max_depth_(options.max_depth),
      depth_(static_cast<int>(g.edge_count()) - static_cast<int>(h.edge_count())),
      g_(std::move(g)),
      h_(std::move(h)),
      edge_mapping_(h_.edge_count()),
      edge_node_mapping_(h_.edge_count()),
      g_free_edges_(all_edges(g_)) {
    if (max_depth_) {
        if (*max_depth_ < 0) {
            throw std::invalid_argument("max_depth must be non-negative");
        }
        depth_ = std::min(depth_, *max_depth_);
    }

    priority_ = options.use_random_priority ? get_random_edge_priority() : get_edge_priority();
}

bool QuickImmersion::execute(int end_depth, std::size_t end_amount) {
    end_depth_ = end_depth;
    end_amount_ = end_amount;
    best_immersions_.clear();

    const int maximum_depth = static_cast<int>(g_.edge_count()) - static_cast<int>(h_.edge_count());
    if (maximum_depth < 0 || h_.edge_count() == 0) {
        return false;
    }

    if (max_depth_) {
        reset_search_state();
        (void)initialize();
    } else {
        // Start with a small upper bound instead of the full |E(G)| - |E(H)|
        // budget.  The full budget is often enormous and leads the search into
        // oversized edge images before it finds a low-depth witness.
        constexpr int initial_unbounded_depth = 3;
        const int first_depth = std::min(initial_unbounded_depth, maximum_depth);
        for (int search_depth = first_depth; search_depth <= maximum_depth; ++search_depth) {
            depth_ = search_depth;
            reset_search_state();
            if (initialize() || !best_immersions_.empty()) {
                break;
            }
        }
    }

    reset_search_state();
    end_depth_ = 0;
    end_amount_ = 100;
    return !best_immersions_.empty();
}

EdgeList QuickImmersion::get_edge_priority() const {
    EdgeList remaining = all_edges(h_);
    if (remaining.empty()) {
        return {};
    }

    EdgeId first = remaining.front();
    for (const auto edge : remaining) {
        if (h_.edge_vertices(edge).size() > h_.edge_vertices(first).size() ||
            (h_.edge_vertices(edge).size() == h_.edge_vertices(first).size() && edge < first)) {
            first = edge;
        }
    }

    EdgeList priority{first};
    erase_value(remaining, first);
    VertexList included_nodes = h_.edge_vertices(first);

    while (!remaining.empty()) {
        EdgeId best = remaining.front();
        auto best_overlap = set_intersection_vec(h_.edge_vertices(best), included_nodes).size();
        for (const auto edge : remaining) {
            const auto overlap = set_intersection_vec(h_.edge_vertices(edge), included_nodes).size();
            if (overlap > best_overlap ||
                (overlap == best_overlap && h_.edge_vertices(edge).size() > h_.edge_vertices(best).size()) ||
                (overlap == best_overlap && h_.edge_vertices(edge).size() == h_.edge_vertices(best).size() && edge < best)) {
                best = edge;
                best_overlap = overlap;
            }
        }

        priority.push_back(best);
        included_nodes = set_union_vec(included_nodes, h_.edge_vertices(best));
        erase_value(remaining, best);
    }

    return priority;
}

EdgeList QuickImmersion::get_random_edge_priority() const {
    // Deterministic fallback: Python's random variant depends on set pop order.
    // Keep a connected-adjacency walk when possible, and fall back to numeric order.
    EdgeList remaining = all_edges(h_);
    if (remaining.empty()) {
        return {};
    }

    EdgeList priority{remaining.front()};
    erase_value(remaining, priority.front());
    EdgeList next_edges = h_.adjacent_edges(priority.front());

    while (!remaining.empty()) {
        auto candidates = set_intersection_vec(next_edges, remaining);
        const EdgeId next = candidates.empty() ? remaining.front() : candidates.front();
        priority.push_back(next);
        erase_value(remaining, next);
        next_edges = set_union_vec(next_edges, h_.adjacent_edges(next));
    }

    return priority;
}

void QuickImmersion::reset_search_state() {
    match_ = Matching{};
    edge_mapping_.assign(h_.edge_count(), {});
    edge_node_mapping_.assign(h_.edge_count(), {});
    history_.clear();
    map_depth_ = 0;
    priority_index_ = 0;
    merges_ = 0;
    g_free_edges_ = all_edges(g_);
}

void QuickImmersion::save(EdgeId g_edge) {
    erase_value(g_free_edges_, g_edge);
    history_.push_back(Snapshot{match_, edge_mapping_, edge_node_mapping_, g_edge});
    ++map_depth_;
}

void QuickImmersion::revert() {
    if (map_depth_ <= 0 || history_.empty()) {
        throw std::logic_error("cannot revert an empty QuickImmersion history");
    }

    --map_depth_;
    auto snapshot = std::move(history_.back());
    history_.pop_back();

    const auto current_h_edge = priority_[static_cast<std::size_t>(priority_index_)];
    if (!snapshot.edge_mapping[static_cast<std::size_t>(current_h_edge)].empty()) {
        --merges_;
    }

    match_ = std::move(snapshot.match);
    edge_mapping_ = std::move(snapshot.edge_mapping);
    edge_node_mapping_ = std::move(snapshot.edge_node_mapping);
    insert_unique(g_free_edges_, snapshot.g_edge_added);
}

void QuickImmersion::add_g_edge(EdgeId g_edge) {
    const auto h_edge = priority_[static_cast<std::size_t>(priority_index_)];
    auto& current_edge_mapping = edge_mapping_[static_cast<std::size_t>(h_edge)];

    if (!current_edge_mapping.empty()) {
        ++merges_;
    }

    save(g_edge);

    if (current_edge_mapping.empty()) {
        for (const auto h_node : h_.edge_vertices(h_edge)) {
            if (match_.has_h_node(h_node)) {
                const auto neighbors = match_.h_node_neighbors(h_node);
                for (const auto g_node : neighbors) {
                    if (!contains(g_.edge_vertices(g_edge), g_node)) {
                        match_.remove_edge(h_node, g_node);
                    }
                }
            } else {
                match_.add_h_node(h_node);
            }
        }
    }

    auto& current_node_mapping = edge_node_mapping_[static_cast<std::size_t>(h_edge)];
    for (const auto g_node : g_.edge_vertices(g_edge)) {
        if (contains(current_node_mapping, g_node)) {
            continue;
        }
        insert_unique(current_node_mapping, g_node);
        for (const auto h_node : h_.edge_vertices(h_edge)) {
            bool linked = true;
            for (const auto incident_h_edge : h_.incident_edges(h_node)) {
                if (incident_h_edge == h_edge) {
                    continue;
                }
                if (!contains(edge_node_mapping_[static_cast<std::size_t>(incident_h_edge)], g_node)) {
                    linked = false;
                    break;
                }
            }
            if (linked) {
                match_.add_edge(h_node, g_node);
            }
        }
    }

    insert_unique(current_edge_mapping, g_edge);
}

bool QuickImmersion::write(ImmersionFunction immersion) {
    const auto alpha_depth = static_cast<int>(immersion.cost()) - static_cast<int>(h_.edge_count());
    if (alpha_depth > depth_) {
        throw std::logic_error("created an immersion outside current depth bounds");
    }

    if (alpha_depth < depth_ && smart_depth_) {
        depth_ = alpha_depth;
        best_immersions_.clear();
        best_immersions_.push_back(std::move(immersion));
        return depth_ <= end_depth_ && 1 >= end_amount_;
    }

    best_immersions_.push_back(std::move(immersion));
    return depth_ <= end_depth_ && best_immersions_.size() >= end_amount_;
}

bool QuickImmersion::node_mapping() {
    auto match = match_.match();
    if (!match) {
        return false;
    }

    for (const auto h_node : all_vertices(h_)) {
        if (match->find(h_node) == match->end()) {
            return false;
        }
    }

    auto edge_mapping = edge_mapping_;
    ImmersionFunction immersion(*match, std::move(edge_mapping), g_, h_);
    if (!immersion.is_immersion()) {
        return false;
    }
    return write(std::move(immersion));
}

bool QuickImmersion::initialize() {
    EdgeList whitelist = all_edges(g_);
    EdgeList blacklist;

    while (!whitelist.empty()) {
        const auto g_edge = whitelist.back();
        whitelist.pop_back();
        insert_unique(blacklist, g_edge);
        add_g_edge(g_edge);
        if (initialize_branching(set_intersection_vec(whitelist, g_.adjacent_edges(g_edge)), blacklist, false, {})) {
            return true;
        }
    }
    return false;
}

bool QuickImmersion::initialize_branching(
    EdgeList whitelist,
    EdgeList blacklist,
    bool just_reset,
    EdgeList current_branching) {
    const auto h_edge = priority_.front();
    if (!just_reset && h_.edge_vertices(h_edge).size() <= edge_node_mapping_[static_cast<std::size_t>(h_edge)].size()) {
        if (immerse_next_edge()) {
            return true;
        }
    }

    if (depth_ >= static_cast<int>(edge_mapping_[static_cast<std::size_t>(h_edge)].size())) {
        if (!current_branching.empty()) {
            const auto new_blacklist = set_union_vec(blacklist, whitelist);
            EdgeList new_whitelist;
            for (const auto g_edge : current_branching) {
                new_whitelist = set_union_vec(new_whitelist, g_.adjacent_edges(g_edge));
            }
            new_whitelist = set_difference_vec(new_whitelist, new_blacklist);
            if (!new_whitelist.empty() && initialize_branching(new_whitelist, new_blacklist, true, {})) {
                return true;
            }
        }

        while (!whitelist.empty()) {
            const auto g_edge = whitelist.back();
            whitelist.pop_back();
            insert_unique(blacklist, g_edge);
            add_g_edge(g_edge);
            if (initialize_branching(whitelist, blacklist, false, set_union_vec(current_branching, EdgeList{g_edge}))) {
                return true;
            }
        }
    }

    if (!just_reset) {
        revert();
    }
    return false;
}

bool QuickImmersion::immerse_next_edge() {
    if (priority_index_ + 1 >= static_cast<int>(h_.edge_count())) {
        return node_mapping();
    }

    ++priority_index_;
    const auto h_edge = priority_[static_cast<std::size_t>(priority_index_)];

    EdgeList mapped_adjacents;
    std::vector<EdgeList> adjacent_list;

    EdgeList previous_priority(priority_.begin(), priority_.begin() + priority_index_);
    const auto adjacent_mapped_h_edges = set_intersection_vec(h_.adjacent_edges(h_edge), previous_priority);
    for (const auto adjacent_h_edge : adjacent_mapped_h_edges) {
        mapped_adjacents = set_union_vec(mapped_adjacents, edge_mapping_[static_cast<std::size_t>(adjacent_h_edge)]);
        EdgeList adjacents;
        for (const auto g_edge : edge_mapping_[static_cast<std::size_t>(adjacent_h_edge)]) {
            adjacents = set_union_vec(adjacents, g_.adjacent_edges(g_edge));
        }
        adjacents = set_intersection_vec(adjacents, g_free_edges_);
        if (adjacents.empty()) {
            --priority_index_;
            return false;
        }
        adjacent_list.push_back(std::move(adjacents));
    }

    if (adjacent_mapped_h_edges.empty()) {
        EdgeList start_edges = g_free_edges_;
        EdgeList blacklist;
        while (!start_edges.empty()) {
            const auto g_edge = start_edges.back();
            start_edges.pop_back();
            insert_unique(blacklist, g_edge);
            add_g_edge(g_edge);

            auto whitelist = set_intersection_vec(g_free_edges_, g_.adjacent_edges(g_edge));
            whitelist = set_difference_vec(whitelist, blacklist);
            if (branch(whitelist, blacklist, {}, {}, false, {})) {
                return true;
            }
        }

        --priority_index_;
        return false;
    }

    EdgeList blob;
    for (const auto g_edge : mapped_adjacents) {
        blob = set_union_vec(blob, g_.adjacent_edges(g_edge));
    }
    blob = set_intersection_vec(blob, g_free_edges_);

    EdgeList blacklist;
    while (!blob.empty()) {
        const auto g_edge = blob.back();
        blob.pop_back();
        insert_unique(blacklist, g_edge);
        add_g_edge(g_edge);

        std::vector<EdgeList> branch_adjacents;
        for (const auto& adjacent_set : adjacent_list) {
            if (!contains(adjacent_set, g_edge)) {
                branch_adjacents.push_back(adjacent_set);
            }
        }

        auto whitelist = set_intersection_vec(g_free_edges_, g_.adjacent_edges(g_edge));
        whitelist = set_difference_vec(whitelist, blacklist);
        if (branch(whitelist, blacklist, blob, branch_adjacents, false, {})) {
            return true;
        }
    }

    --priority_index_;
    return false;
}

bool QuickImmersion::branch(
    EdgeList whitelist,
    EdgeList blacklist,
    EdgeList blob,
    std::vector<EdgeList> adjacents,
    bool just_reset,
    EdgeList current_branching) {
    const auto h_edge = priority_[static_cast<std::size_t>(priority_index_)];
    if (!just_reset && adjacents.empty() &&
        h_.edge_vertices(h_edge).size() <= edge_node_mapping_[static_cast<std::size_t>(h_edge)].size()) {
        if (immerse_next_edge()) {
            return true;
        }
    }

    if (depth_ > merges_) {
        if (!current_branching.empty()) {
            const auto new_blacklist = set_union_vec(blacklist, whitelist);
            EdgeList new_whitelist;
            for (const auto g_edge : current_branching) {
                new_whitelist = set_union_vec(new_whitelist, g_.adjacent_edges(g_edge));
            }
            new_whitelist = set_difference_vec(new_whitelist, new_blacklist);
            new_whitelist = set_intersection_vec(new_whitelist, g_free_edges_);
            if (!new_whitelist.empty() && branch(new_whitelist, new_blacklist, blob, adjacents, true, {})) {
                return true;
            }
        }

        while (!whitelist.empty()) {
            const auto g_edge = whitelist.back();
            whitelist.pop_back();
            insert_unique(blacklist, g_edge);
            add_g_edge(g_edge);

            auto new_blob = blob;
            auto new_adjacents = adjacents;
            if (contains(blob, g_edge)) {
                erase_value(new_blob, g_edge);
                new_adjacents.clear();
                for (const auto& adjacent_set : adjacents) {
                    if (!contains(adjacent_set, g_edge)) {
                        new_adjacents.push_back(adjacent_set);
                    }
                }
            }

            if (branch(whitelist, blacklist, new_blob, new_adjacents, false, set_union_vec(current_branching, EdgeList{g_edge}))) {
                return true;
            }
        }
    }

    if (!just_reset) {
        revert();
    }
    return false;
}

} // namespace fhi
