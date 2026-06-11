#pragma once

#include <cstdint>
#include <vector>

namespace fhi {

using VertexId = std::int32_t;
using EdgeId = std::int32_t;

using VertexList = std::vector<VertexId>;
using EdgeList = std::vector<EdgeId>;

} // namespace fhi
