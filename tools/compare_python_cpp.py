#!/usr/bin/env python3
"""Compare the original Python quick_immersion solver with the C++ CLI.

The original project requires NetworkX. If it is not installed, this script exits
with status 77 so build systems can treat the regression as skipped.
"""

from __future__ import annotations

import argparse
import itertools
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

try:
    from Hypergraph import hypergraph
    from Quick_immersion import quick_immersion
except ModuleNotFoundError as error:
    print(f"SKIP: Python dependency missing: {error}", file=sys.stderr)
    sys.exit(77)


def all_nonempty_edges(vertex_count: int) -> list[set[int]]:
    vertices = list(range(vertex_count))
    edges: list[set[int]] = []
    for size in range(1, vertex_count + 1):
        for combo in itertools.combinations(vertices, size):
            edges.append(set(combo))
    return edges


def generated_hypergraphs(vertex_count: int, max_edges: int) -> list[hypergraph]:
    edge_pool = all_nonempty_edges(vertex_count)
    graphs: list[hypergraph] = []
    seen: set[str] = set()
    for edge_count in range(1, max_edges + 1):
        for edge_combo in itertools.combinations(range(len(edge_pool)), edge_count):
            edges = {i: edge_pool[index].copy() for i, index in enumerate(edge_combo)}
            nodes = set().union(*edges.values())
            graph = hypergraph(nodes, edges)
            graph.skim()
            if graph.node_count == 0 or graph.hyperedge_count == 0:
                continue
            graph.minimize_assignments()
            encoded = graph.store(sort=True)
            if encoded not in seen and graph.hyperedge_count > 0:
                seen.add(encoded)
                graphs.append(graph)
    return graphs


def python_result(g: hypergraph, h: hypergraph, max_depth: int | None) -> bool:
    solver = quick_immersion(g, h, max_depth=max_depth)
    return solver.execute()


def cpp_result(cli: Path, g: hypergraph, h: hypergraph, max_depth: int | None) -> bool:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        h_path = tmp / "h.hg"
        g_path = tmp / "g.hg"
        h_path.write_text(h.store(sort=True) + "\n", encoding="utf-8")
        g_path.write_text(g.store(sort=True) + "\n", encoding="utf-8")
        command = [str(cli), "--pattern", str(h_path), "--target", str(g_path)]
        if max_depth is not None:
            command += ["--max-depth", str(max_depth)]
        completed = subprocess.run(command, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode != 0:
        raise RuntimeError(f"C++ solver failed with {completed.returncode}: {completed.stderr}")
    first_line = completed.stdout.splitlines()[0].strip()
    if first_line == "YES":
        return True
    if first_line == "NO":
        return False
    raise RuntimeError(f"unexpected C++ solver output: {completed.stdout!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", type=Path, default=Path("build/fhi_cli"))
    parser.add_argument("--vertices", type=int, default=3)
    parser.add_argument("--max-edges", type=int, default=3)
    parser.add_argument("--max-pairs", type=int, default=250)
    parser.add_argument("--max-depth", type=int, default=None)
    args = parser.parse_args()

    if not args.cli.exists():
        print(f"C++ CLI not found: {args.cli}", file=sys.stderr)
        return 2

    graphs = generated_hypergraphs(args.vertices, args.max_edges)
    checked = 0
    for g in graphs:
        for h in graphs:
            if g.node_count < h.node_count or g.hyperedge_count < h.hyperedge_count:
                continue
            py = python_result(g.copy(), h.copy(), args.max_depth)
            cpp = cpp_result(args.cli, g, h, args.max_depth)
            checked += 1
            if py != cpp:
                print("MISMATCH")
                print(f"G={g.store(sort=True)}")
                print(f"H={h.store(sort=True)}")
                print(f"python={py}")
                print(f"cpp={cpp}")
                return 1
            if checked >= args.max_pairs:
                print(f"OK: checked {checked} graph pairs")
                return 0

    print(f"OK: checked {checked} graph pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
