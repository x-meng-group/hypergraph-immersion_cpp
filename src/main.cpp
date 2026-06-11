#include "fhi/Parser.hpp"
#include "fhi/QuickImmersion.hpp"

#include <exception>
#include <iostream>
#include <string>

namespace {

void print_usage(const char* executable) {
    std::cerr
        << "Usage:\n"
        << "  " << executable << " --inspect <encoded-hypergraph-file>\n"
        << "  " << executable << " --pattern <H-file> --target <G-file> [--max-depth N]\n"
        << "\n"
        << "Files use the Python-compatible encoded hypergraph format.\n";
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
        fhi::QuickImmersionOptions options;
        for (int i = 1; i < argc; ++i) {
            const std::string arg = argv[i];
            if (arg == "--pattern" && i + 1 < argc) {
                pattern_path = argv[++i];
            } else if (arg == "--target" && i + 1 < argc) {
                target_path = argv[++i];
            } else if (arg == "--max-depth" && i + 1 < argc) {
                options.max_depth = std::stoi(argv[++i]);
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
        fhi::QuickImmersion solver(g, h, options);
        const bool found = solver.execute();
        std::cout << (found ? "YES" : "NO") << '\n';
        if (found) {
            std::cout << "cost: " << solver.immersions().front().cost() << '\n';
            std::cout << "count: " << solver.immersions().size() << '\n';
        }
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
