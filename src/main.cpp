#include "fhi/Parser.hpp"
#include "fhi/QuickImmersion.hpp"

#include <exception>
#include <fstream>
#include <iostream>
#include <limits>
#include <map>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>

namespace {

void print_usage(const char* executable) {
    std::cerr
        << "Usage:\n"
        << "  " << executable << " --inspect <encoded-hypergraph-file>\n"
        << "  " << executable << " --pattern <H-file> --target <G-file> [--max-depth N] [--print-mapping-json]\n"
        << "  " << executable << " --pattern <H-file> --target <G-file> --validate-mapping <mapping-file>\n"
        << "\n"
        << "Files use the Python-compatible encoded hypergraph format.\n";
}

std::vector<int> parse_csv_ints(const std::string& line) {
    std::vector<int> values;
    std::stringstream stream(line);
    std::string token;
    while (std::getline(stream, token, ',')) {
        if (!token.empty()) {
            values.push_back(std::stoi(token));
        }
    }
    return values;
}

fhi::ImmersionFunction read_mapping_file(
    const std::string& path,
    const fhi::Hypergraph& g,
    const fhi::Hypergraph& h) {
    std::ifstream input(path);
    if (!input) {
        throw std::runtime_error("failed to open mapping file for reading: " + path);
    }

    std::string node_line;
    if (!std::getline(input, node_line)) {
        throw std::runtime_error("mapping file is missing node mapping line");
    }
    const auto node_values = parse_csv_ints(node_line);
    if (node_values.size() != h.vertex_count()) {
        throw std::runtime_error("mapping file node count does not match H");
    }

    std::unordered_map<fhi::VertexId, fhi::VertexId> node_mapping;
    for (std::size_t h_node = 0; h_node < node_values.size(); ++h_node) {
        node_mapping.emplace(static_cast<fhi::VertexId>(h_node), node_values[h_node]);
    }

    std::vector<fhi::EdgeList> edge_mapping;
    std::string edge_line;
    while (std::getline(input, edge_line)) {
        edge_mapping.push_back(parse_csv_ints(edge_line));
    }
    if (edge_mapping.size() != h.edge_count()) {
        throw std::runtime_error("mapping file edge count does not match H");
    }

    return fhi::ImmersionFunction(std::move(node_mapping), std::move(edge_mapping), g, h);
}

void print_edge_list_json(const fhi::EdgeList& edges) {
    std::cout << '[';
    for (std::size_t i = 0; i < edges.size(); ++i) {
        if (i != 0) {
            std::cout << ',';
        }
        std::cout << edges[i];
    }
    std::cout << ']';
}

void print_mapping_json(const fhi::ImmersionFunction& immersion) {
    std::map<fhi::VertexId, fhi::VertexId> sorted_node_mapping(
        immersion.node_mapping().begin(),
        immersion.node_mapping().end());

    std::cout << "{\n";
    std::cout << "  \"cost\": " << immersion.cost() << ",\n";
    std::cout << "  \"vertex_mapping\": {";
    bool first = true;
    for (const auto& [h_node, g_node] : sorted_node_mapping) {
        if (!first) {
            std::cout << ',';
        }
        first = false;
        std::cout << "\n    \"" << h_node << "\": " << g_node;
    }
    if (!sorted_node_mapping.empty()) {
        std::cout << '\n';
    }
    std::cout << "  },\n";

    std::cout << "  \"edge_mapping\": {";
    const auto& edge_mapping = immersion.edge_mapping();
    for (std::size_t edge = 0; edge < edge_mapping.size(); ++edge) {
        if (edge != 0) {
            std::cout << ',';
        }
        std::cout << "\n    \"" << edge << "\": ";
        print_edge_list_json(edge_mapping[edge]);
    }
    if (!edge_mapping.empty()) {
        std::cout << '\n';
    }
    std::cout << "  }\n";
    std::cout << "}\n";
}

} // namespace

int main(int argc, char** argv) {
    try {
        if (argc == 3 && std::string(argv[1]) == "--inspect") {
            const auto graph = fhi::read_encoded_hypergraph_file(argv[2]);
            std::cout << "vertices: " << graph.vertex_count() << '\n';
            std::cout << "edges: " << graph.edge_count() << '\n';
            std::cout << "encoded: " << graph.to_encoded_string(true) << '\n';
            std::cout << graph << '\n';
            return 0;
        }

        std::string pattern_path;
        std::string target_path;
        std::string validate_mapping_path;
        bool print_mapping_json_output = false;
        fhi::QuickImmersionOptions options;
        for (int i = 1; i < argc; ++i) {
            const std::string arg = argv[i];
            if (arg == "--pattern" && i + 1 < argc) {
                pattern_path = argv[++i];
            } else if (arg == "--target" && i + 1 < argc) {
                target_path = argv[++i];
            } else if (arg == "--max-depth" && i + 1 < argc) {
                options.max_depth = std::stoi(argv[++i]);
            } else if (arg == "--print-mapping-json") {
                print_mapping_json_output = true;
            } else if (arg == "--validate-mapping" && i + 1 < argc) {
                validate_mapping_path = argv[++i];
            } else {
                print_usage(argv[0]);
                return 2;
            }
        }

        if (pattern_path.empty() || target_path.empty()) {
            print_usage(argv[0]);
            return 2;
        }

        const auto h = fhi::read_encoded_hypergraph_file(pattern_path);
        const auto g = fhi::read_encoded_hypergraph_file(target_path);
        if (!validate_mapping_path.empty()) {
            const auto immersion = read_mapping_file(validate_mapping_path, g, h);
            const bool valid = immersion.is_immersion();
            std::cout << (valid ? "VALID" : "INVALID") << '\n';
            std::cout << "cost: " << immersion.cost() << '\n';
            return valid ? 0 : 1;
        }

        fhi::QuickImmersion solver(g, h, options);
        const bool found = print_mapping_json_output
            ? solver.execute(std::numeric_limits<int>::max(), 1)
            : solver.execute();
        std::cout << (found ? "YES" : "NO") << '\n';
        if (found) {
            std::cout << "cost: " << solver.immersions().front().cost() << '\n';
            std::cout << "count: " << solver.immersions().size() << '\n';
            if (print_mapping_json_output) {
                print_mapping_json(solver.immersions().front());
            }
        }
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
