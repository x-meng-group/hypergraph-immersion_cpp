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
```

It prints `YES` when an immersion is found and `NO` otherwise.

## Layout

- `include/fhi/`: public C++ headers
- `src/`: implementation and CLI entry point
- `tests/`: regression tests
- `benchmarks/`: benchmark notes and future benchmark fixtures
