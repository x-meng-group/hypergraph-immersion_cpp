#include "fhi/Parser.hpp"

#include <fstream>
#include <stdexcept>

namespace fhi {

Hypergraph read_encoded_hypergraph_file(const std::filesystem::path& path) {
    std::ifstream input(path);
    if (!input) {
        throw std::runtime_error("failed to open hypergraph file for reading: " + path.string());
    }

    std::string encoded;
    input >> encoded;
    if (encoded.empty()) {
        throw std::runtime_error("hypergraph file is empty: " + path.string());
    }
    return Hypergraph::from_encoded_string(encoded);
}

void write_encoded_hypergraph_file(const std::filesystem::path& path, const Hypergraph& hypergraph) {
    std::ofstream output(path);
    if (!output) {
        throw std::runtime_error("failed to open hypergraph file for writing: " + path.string());
    }
    output << hypergraph.to_encoded_string(true) << '\n';
}

} // namespace fhi
