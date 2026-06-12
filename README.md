# FastHypergraphImmersion

C++ implementation of a hypergraph immersion solver.

The solver supports disconnected pattern hypergraphs `H` and disconnected target
hypergraphs `G`. When a new disconnected component of `H` is reached, the search
can seed that component from any unused edge of `G`, so components of `H` may map
into separate target components or into disjoint edge sets of the same target
component.

## Build

Use CMake:

```bash
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

Or use the fallback Makefile:

```bash
make
make test
```

## CLI

The command-line tool reads encoded hypergraph files.

```bash
build/fhi_cli --inspect graph.hg
build/fhi_cli --pattern H.hg --target G.hg
build/fhi_cli --pattern H.hg --target G.hg --max-depth 2
build/fhi_cli --pattern H.hg --target G.hg --print-mapping-json
```

It prints `YES` when an immersion is found and `NO` otherwise.

Use `--print-mapping-json` to print one exact immersion mapping:

```json
{
  "cost": 12,
  "vertex_mapping": {
    "0": 94,
    "1": 86
  },
  "edge_mapping": {
    "0": [193, 195],
    "1": [86]
  }
}
```

`vertex_mapping` maps each vertex id of `H` to a vertex id of `G`.
`edge_mapping` maps each edge id of `H` to the connected list of edge ids of
`G` used as its image.

The CLI can also validate a saved plain-text mapping:

```bash
build/fhi_cli --pattern H.hg --target G.hg --validate-mapping mapping.txt
```

The plain-text mapping format is:

```text
<G image of H vertex 0>,<G image of H vertex 1>,...
<comma-separated G edge ids for H edge 0>
<comma-separated G edge ids for H edge 1>
...
```

## Layout

- `include/fhi/`: public C++ headers
- `src/`: implementation and CLI entry point
- `tests/`: regression tests
- `benchmarks/`: benchmark notes and future benchmark fixtures
