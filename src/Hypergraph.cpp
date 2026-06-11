#include "fhi/Hypergraph.hpp"

#include <algorithm>
#include <map>
#include <ostream>
#include <queue>
#include <stdexcept>
#include <unordered_set>

namespace fhi {
namespace {

std::uint32_t read_binary_reversed(const std::string& bitstring) {
    std::uint32_t power = 1;
    std::uint32_t value = 0;
    for (const char bit : bitstring) {
        if (bit == '1') {
            value += power;
        } else if (bit != '0') {
            throw std::invalid_argument("encoded hypergraph contains a non-binary digit");
        }
        power *= 2;
    }
    return value;
}

std::size_t bit_count(std::size_t n) {
    std::size_t count = 1;
    std::size_t max_value = 2;
    while (max_value <= n) {
        ++count;
        max_value *= 2;
    }
    return count;
}

std::string binary_reversed(std::size_t n, std::size_t width) {
    std::string bits;
    bits.reserve(width);
    for (std::size_t i = 0; i < width; ++i) {
        bits.push_back((n % 2 == 1) ? '1' : '0');
        n /= 2;
    }
    return bits;
}

template <class T>
void sort_unique(std::vector<T>& values) {
    std::sort(values.begin(), values.end());
    values.erase(std::unique(values.begin(), values.end()), values.end());
}

} // namespace

Hypergraph::Hypergraph(std::vector<VertexList> edges)
    : edges_(std::move(edges)) {
    normalize_edges();
    rebuild_indexes();
}

Hypergraph Hypergraph::from_encoded_string(const std::string& encoded) {
    const auto separator = encoded.find('-');
    if (separator == std::string::npos || separator == 0) {
        throw std::invalid_argument("encoded hypergraph must have '<bitcount>-<edges>' format");
    }

    const auto width = read_binary_reversed(encoded.substr(0, separator));
    if (width == 0) {
        throw std::invalid_argument("encoded hypergraph bit width must be positive");
    }

    std::vector<VertexList> edges;
    std::unordered_map<std::string, VertexId> bits_to_vertices;
    std::size_t begin = separator + 1;
    while (begin <= encoded.size()) {
        const auto end = encoded.find('.', begin);
        const auto edge_string = encoded.substr(begin, end == std::string::npos ? std::string::npos : end - begin);
        if (edge_string.size() % width != 0) {
            throw std::invalid_argument("encoded hyperedge length is not divisible by bit width");
        }

        VertexList edge;
        for (std::size_t i = 0; i < edge_string.size(); i += width) {
            const auto bits = edge_string.substr(i, width);
            auto it = bits_to_vertices.find(bits);
            if (it == bits_to_vertices.end()) {
                const auto vertex = static_cast<VertexId>(read_binary_reversed(bits));
                it = bits_to_vertices.emplace(bits, vertex).first;
            }
            edge.push_back(it->second);
        }
        edges.push_back(std::move(edge));

        if (end == std::string::npos) {
            break;
        }
        begin = end + 1;
    }

    return Hypergraph(std::move(edges));
}

std::string Hypergraph::to_encoded_string(bool sort_edges) const {
    if (incident_edges_.empty()) {
        return "1-";
    }

    const auto width = bit_count(incident_edges_.size() - 1);
    std::vector<std::string> vertex_bits;
    vertex_bits.reserve(incident_edges_.size());
    for (std::size_t vertex = 0; vertex < incident_edges_.size(); ++vertex) {
        vertex_bits.push_back(binary_reversed(vertex, width));
    }

    EdgeList edge_order;
    edge_order.reserve(edges_.size());
    for (EdgeId edge = 0; edge < static_cast<EdgeId>(edges_.size()); ++edge) {
        edge_order.push_back(edge);
    }
    if (sort_edges) {
        std::sort(edge_order.begin(), edge_order.end(), [this](EdgeId lhs, EdgeId rhs) {
            return edges_[lhs] < edges_[rhs];
        });
    }

    std::string encoded = binary_reversed(width, bit_count(width));
    encoded.push_back('-');
    bool first = true;
    for (const auto edge : edge_order) {
        if (!first) {
            encoded.push_back('.');
        }
        first = false;
        for (const auto vertex : edges_[edge]) {
            encoded += vertex_bits[static_cast<std::size_t>(vertex)];
        }
    }
    return encoded;
}

const VertexList& Hypergraph::edge_vertices(EdgeId edge) const {
    validate_edge(edge);
    return edges_[static_cast<std::size_t>(edge)];
}

const EdgeList& Hypergraph::incident_edges(VertexId vertex) const {
    validate_vertex(vertex);
    return incident_edges_[static_cast<std::size_t>(vertex)];
}

const EdgeList& Hypergraph::adjacent_edges(EdgeId edge) const {
    validate_edge(edge);
    return edge_adjacency_[static_cast<std::size_t>(edge)];
}

VertexList Hypergraph::vertices_of_edges(const EdgeList& edge_ids) const {
    VertexList vertices;
    for (const auto edge : edge_ids) {
        validate_edge(edge);
        vertices.insert(vertices.end(), edges_[static_cast<std::size_t>(edge)].begin(), edges_[static_cast<std::size_t>(edge)].end());
    }
    sort_unique(vertices);
    return vertices;
}

bool Hypergraph::is_connected(const EdgeList& edge_ids) const {
    if (edge_ids.empty()) {
        return false;
    }

    std::unordered_set<EdgeId> remaining(edge_ids.begin(), edge_ids.end());
    for (const auto edge : edge_ids) {
        validate_edge(edge);
    }

    std::queue<EdgeId> queue;
    queue.push(*remaining.begin());
    remaining.erase(*remaining.begin());

    while (!queue.empty()) {
        const auto edge = queue.front();
        queue.pop();
        for (const auto adjacent : edge_adjacency_[static_cast<std::size_t>(edge)]) {
            const auto it = remaining.find(adjacent);
            if (it != remaining.end()) {
                queue.push(adjacent);
                remaining.erase(it);
            }
        }
    }

    return remaining.empty();
}

EdgeId Hypergraph::largest_edge(const EdgeList& edge_ids) const {
    if (edge_ids.empty()) {
        throw std::invalid_argument("largest_edge requires a non-empty edge list");
    }

    EdgeId largest = edge_ids.front();
    validate_edge(largest);
    for (const auto edge : edge_ids) {
        validate_edge(edge);
        if (edges_[static_cast<std::size_t>(edge)].size() > edges_[static_cast<std::size_t>(largest)].size()) {
            largest = edge;
        }
    }
    return largest;
}

std::vector<EdgeList> Hypergraph::clusters(const EdgeList& edge_ids) const {
    std::unordered_set<EdgeId> remaining(edge_ids.begin(), edge_ids.end());
    for (const auto edge : edge_ids) {
        validate_edge(edge);
    }

    std::vector<EdgeList> result;
    while (!remaining.empty()) {
        EdgeList cluster;
        std::queue<EdgeId> queue;
        queue.push(*remaining.begin());
        remaining.erase(*remaining.begin());

        while (!queue.empty()) {
            const auto edge = queue.front();
            queue.pop();
            cluster.push_back(edge);
            for (const auto adjacent : edge_adjacency_[static_cast<std::size_t>(edge)]) {
                const auto it = remaining.find(adjacent);
                if (it != remaining.end()) {
                    queue.push(adjacent);
                    remaining.erase(it);
                }
            }
        }

        std::sort(cluster.begin(), cluster.end());
        result.push_back(std::move(cluster));
    }

    return result;
}

bool Hypergraph::operator==(const Hypergraph& other) const noexcept {
    return edges_ == other.edges_;
}

void Hypergraph::normalize_edges() {
    VertexList used_vertices;
    for (auto& edge : edges_) {
        for (const auto vertex : edge) {
            if (vertex < 0) {
                throw std::invalid_argument("hypergraph vertex ids must be non-negative");
            }
            used_vertices.push_back(vertex);
        }
        sort_unique(edge);
    }

    sort_unique(used_vertices);
    std::map<VertexId, VertexId> compact_ids;
    for (VertexId compact = 0; compact < static_cast<VertexId>(used_vertices.size()); ++compact) {
        compact_ids[used_vertices[static_cast<std::size_t>(compact)]] = compact;
    }

    for (auto& edge : edges_) {
        for (auto& vertex : edge) {
            vertex = compact_ids.at(vertex);
        }
        sort_unique(edge);
    }

    if (!used_vertices.empty()) {
        incident_edges_.resize(used_vertices.size());
    }
}

void Hypergraph::rebuild_indexes() {
    for (auto& incident : incident_edges_) {
        incident.clear();
    }

    for (EdgeId edge = 0; edge < static_cast<EdgeId>(edges_.size()); ++edge) {
        for (const auto vertex : edges_[static_cast<std::size_t>(edge)]) {
            incident_edges_[static_cast<std::size_t>(vertex)].push_back(edge);
        }
    }

    edge_adjacency_.assign(edges_.size(), {});
    for (const auto& incident : incident_edges_) {
        for (std::size_t i = 0; i < incident.size(); ++i) {
            for (std::size_t j = i + 1; j < incident.size(); ++j) {
                edge_adjacency_[static_cast<std::size_t>(incident[i])].push_back(incident[j]);
                edge_adjacency_[static_cast<std::size_t>(incident[j])].push_back(incident[i]);
            }
        }
    }

    for (auto& adjacent : edge_adjacency_) {
        sort_unique(adjacent);
    }
}

void Hypergraph::validate_edge(EdgeId edge) const {
    if (edge < 0 || static_cast<std::size_t>(edge) >= edges_.size()) {
        throw std::out_of_range("edge id is outside this hypergraph");
    }
}

void Hypergraph::validate_vertex(VertexId vertex) const {
    if (vertex < 0 || static_cast<std::size_t>(vertex) >= incident_edges_.size()) {
        throw std::out_of_range("vertex id is outside this hypergraph");
    }
}

std::ostream& operator<<(std::ostream& os, const Hypergraph& hypergraph) {
    os << "{";
    for (std::size_t edge = 0; edge < hypergraph.edges().size(); ++edge) {
        if (edge != 0) {
            os << ", ";
        }
        os << edge << ": {";
        const auto& vertices = hypergraph.edges()[edge];
        for (std::size_t i = 0; i < vertices.size(); ++i) {
            if (i != 0) {
                os << ", ";
            }
            os << vertices[i];
        }
        os << "}";
    }
    os << "}";
    return os;
}

} // namespace fhi
