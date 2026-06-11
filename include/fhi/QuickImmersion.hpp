#pragma once

#include "fhi/ImmersionFunction.hpp"
#include "fhi/Matching.hpp"

#include <optional>

namespace fhi {

struct QuickImmersionOptions {
    std::optional<int> max_depth;
    bool use_random_priority = false;
    bool dynamic_depth = true;
};

class QuickImmersion {
public:
    QuickImmersion(Hypergraph g, Hypergraph h, QuickImmersionOptions options = {});

    [[nodiscard]] bool execute(int end_depth = 0, std::size_t end_amount = 100);
    [[nodiscard]] const std::vector<ImmersionFunction>& immersions() const noexcept { return best_immersions_; }
    [[nodiscard]] const EdgeList& priority() const noexcept { return priority_; }

private:
    struct Snapshot {
        Matching match;
        std::vector<EdgeList> edge_mapping;
        std::vector<VertexList> edge_node_mapping;
        EdgeId g_edge_added = -1;
    };

    bool smart_depth_ = true;
    std::optional<int> max_depth_;
    int depth_ = 0;
    Hypergraph g_;
    Hypergraph h_;
    Matching match_;
    std::vector<EdgeList> edge_mapping_;
    std::vector<VertexList> edge_node_mapping_;
    std::vector<Snapshot> history_;
    int map_depth_ = 0;
    EdgeList priority_;
    int priority_index_ = 0;
    int merges_ = 0;
    std::vector<ImmersionFunction> best_immersions_;
    EdgeList g_free_edges_;
    int end_depth_ = 0;
    std::size_t end_amount_ = 100;

    [[nodiscard]] EdgeList get_edge_priority() const;
    [[nodiscard]] EdgeList get_random_edge_priority() const;

    void reset_search_state();
    void save(EdgeId g_edge);
    void revert();
    void add_g_edge(EdgeId g_edge);

    [[nodiscard]] bool write(ImmersionFunction immersion);
    [[nodiscard]] bool node_mapping();
    [[nodiscard]] bool initialize();
    [[nodiscard]] bool initialize_branching(
        EdgeList whitelist,
        EdgeList blacklist,
        bool just_reset,
        EdgeList current_branching);
    [[nodiscard]] bool immerse_next_edge();
    [[nodiscard]] bool branch(
        EdgeList whitelist,
        EdgeList blacklist,
        EdgeList blob,
        std::vector<EdgeList> adjacents,
        bool just_reset,
        EdgeList current_branching);
};

} // namespace fhi
