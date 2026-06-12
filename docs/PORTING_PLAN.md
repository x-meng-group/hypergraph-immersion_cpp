# FastHypergraphImmersion Porting Plan

This repository started as the Python hypergraph immersion implementation in the flat source files at the repository root. The C++ port lives under `include/`, `src/`, `tests/`, `benchmarks/`, and `docs/`.

## Python To C++ Map

- `Hypergraph.py` -> `fhi::Hypergraph`
- `Matching.py` -> `fhi::Matching`
- `Immersion_function.py` -> `fhi::ImmersionFunction`
- `Quick_immersion.py` -> `fhi::QuickImmersion`
- `Immersion.py` -> planned baseline/reference solver after `QuickImmersion`
- drawing/scatter/geometry modules -> leave in Python unless visualization performance becomes important

## Current C++ Milestone

The initial C++ foundation includes:

- contiguous integer vertex and edge IDs
- sorted vector storage for hyperedges
- incident-edge and edge-adjacency indexes
- Python-compatible encoded hypergraph parser/writer
- Hopcroft-Karp bipartite matching replacement for NetworkX
- immersion witness validation
- a smoke-test CLI for inspecting encoded hypergraph files
- an initial direct port of `Quick_immersion.py` as `fhi::QuickImmersion`

## Next Porting Target

Validate `fhi::QuickImmersion` against the Python implementation on a broader fixture set. The initial C++ port is intentionally close to Python behavior; the next work should find edge cases before optimizing it.

Important Python state to preserve:

- `__priority`
- `__depth`
- `__max_depth`
- `__smartdepth`
- `__match`
- `__edge_mapping`
- `__edge_node_mapping`
- `__match_history`
- `__edge_mapping_history`
- `__edge_node_mapping_history`
- `__G_edges_added`
- `__G_free_edges`
- `__merges`
- `__priority_index`

## Implementation Strategy

1. Keep behavior close to Python until tests pass.
2. Use vectors and integer IDs instead of Python sets/dicts in hot paths.
3. Only introduce pruning after the direct port has regression coverage.
4. Keep the Python files available as reference until the C++ solver is validated.
5. Benchmark each optimization against the direct C++ port and Python baseline.

## Regression Checks

After building `build/fhi_cli`, compare the C++ quick solver against the Python quick solver:

```bash
python3 tools/compare_python_cpp.py --cli build/fhi_cli --vertices 3 --max-edges 3
```

The Python comparison requires NetworkX because the original implementation imports it. If NetworkX is missing, the script exits with status 77 and prints a skip message.

## Build

```bash
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

If CMake is unavailable, use the local Makefile fallback:

```bash
make
make test
```
