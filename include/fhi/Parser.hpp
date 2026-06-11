#pragma once

#include "fhi/Hypergraph.hpp"

#include <filesystem>
#include <string>

namespace fhi {

Hypergraph read_encoded_hypergraph_file(const std::filesystem::path& path);
void write_encoded_hypergraph_file(const std::filesystem::path& path, const Hypergraph& hypergraph);

} // namespace fhi
