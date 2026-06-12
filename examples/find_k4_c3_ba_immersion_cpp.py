#!/usr/bin/env python3
"""Find a K4 plus C3 immersion in a BA(100,2) graph using the C++ solver."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "examples" / "output" / "k4_c3_ba100"
CLI = REPO_ROOT / "build" / "fhi_cli"
TARGET_VERTEX_COUNT = 100
TARGET_M = 2
SOLVER_TIMEOUT_SECONDS = 45
TARGET_SEED = 16


def bit_count(n: int) -> int:
    count = 1
    max_value = 2
    while max_value <= n:
        count += 1
        max_value *= 2
    return count


def binary_reversed(n: int, width: int) -> str:
    bits = []
    for _ in range(width):
        bits.append("1" if n % 2 == 1 else "0")
        n //= 2
    return "".join(bits)


def encode_hypergraph(edges: list[tuple[int, int]], vertex_count: int, sort_edges: bool = True) -> str:
    width = bit_count(vertex_count - 1)
    vertex_bits = [binary_reversed(vertex, width) for vertex in range(vertex_count)]
    edge_order = sorted(tuple(sorted(edge)) for edge in edges) if sort_edges else [tuple(sorted(edge)) for edge in edges]
    encoded_edges = ["".join(vertex_bits[v] for v in edge) for edge in edge_order]
    return f"{binary_reversed(width, bit_count(width))}-" + ".".join(encoded_edges)


def guest_edges() -> list[tuple[int, int]]:
    k4 = [(u, v) for u in range(4) for v in range(u + 1, 4)]
    c3 = [(4, 5), (4, 6), (5, 6)]
    return k4 + c3


def ba_edges(vertex_count: int, seed: int) -> list[tuple[int, int]]:
    import networkx as nx

    graph = nx.barabasi_albert_graph(vertex_count, TARGET_M, seed=seed)
    return sorted(tuple(sorted(edge)) for edge in graph.edges())


def run_cpp_solver(h_path: Path, g_path: Path) -> dict | None:
    command = [
        str(CLI),
        "--pattern",
        str(h_path),
        "--target",
        str(g_path),
        "--print-mapping-json",
    ]
    try:
        completed = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=SOLVER_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return None

    if completed.returncode != 0 or not completed.stdout.startswith("YES\n"):
        return None

    json_start = completed.stdout.find("{")
    if json_start < 0:
        raise RuntimeError(f"C++ solver did not print mapping JSON:\n{completed.stdout}")
    return json.loads(completed.stdout[json_start:])


def write_cpp_mapping_file(mapping: dict, path: Path) -> None:
    node_values = [str(mapping["vertex_mapping"][str(h_node)]) for h_node in range(7)]
    edge_lines = [
        ",".join(str(edge) for edge in mapping["edge_mapping"][str(h_edge)])
        for h_edge in range(9)
    ]
    path.write_text(",".join(node_values) + "\n" + "\n".join(edge_lines) + "\n", encoding="utf-8")


def validate_with_cpp(h_path: Path, g_path: Path, mapping_path: Path) -> None:
    completed = subprocess.run(
        [
            str(CLI),
            "--pattern",
            str(h_path),
            "--target",
            str(g_path),
            "--validate-mapping",
            str(mapping_path),
        ],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0 or not completed.stdout.startswith("VALID\n"):
        raise RuntimeError(
            "C++ mapping validation failed:\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )


def mathematica_edge_list(edges: list[tuple[int, int]], one_based: bool = True) -> str:
    shift = 1 if one_based else 0
    return "{" + ", ".join(f"{u + shift} \\[UndirectedEdge] {v + shift}" for u, v in edges) + "}"


def mathematica_assoc(mapping: dict[str, int], key_shift: int = 0, value_shift: int = 0) -> str:
    entries = []
    for key, value in sorted(mapping.items(), key=lambda item: int(item[0])):
        entries.append(f"{int(key) + key_shift} -> {int(value) + value_shift}")
    return "<|" + ", ".join(entries) + "|>"


def wl_edge_mapping(edge_mapping: dict[str, list[int]], g_edges: list[tuple[int, int]]) -> str:
    entries = []
    for h_edge, image in sorted(edge_mapping.items(), key=lambda item: int(item[0])):
        rhs_edges = [g_edges[g_edge] for g_edge in image]
        entries.append(f"{int(h_edge) + 1} -> {mathematica_edge_list(rhs_edges, one_based=True)}")
    return "<|" + ", ".join(entries) + "|>"


def nb_string(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def build_data(seed: int, mapping: dict, g_edges: list[tuple[int, int]]) -> dict:
    h_edges = guest_edges()
    return {
        "seed": seed,
        "model": f"BarabasiAlbertGraph[{TARGET_VERTEX_COUNT}, {TARGET_M}]",
        "H": "CompleteGraph[4] + CycleGraph[3]",
        "H_vertex_count": 7,
        "H_edge_count": len(h_edges),
        "G_vertex_count": TARGET_VERTEX_COUNT,
        "G_edge_count": len(g_edges),
        "solver": "fhi_cli --print-mapping-json",
        "max_depth": None,
        "cost": mapping["cost"],
        "vertex_mapping": mapping["vertex_mapping"],
        "H_edges": {str(i): list(edge) for i, edge in enumerate(h_edges)},
        "G_edges": {str(i): list(edge) for i, edge in enumerate(g_edges)},
        "edge_mapping": mapping["edge_mapping"],
        "edge_mapping_as_G_edges": {
            h_edge: [list(g_edges[g_edge]) for g_edge in image]
            for h_edge, image in mapping["edge_mapping"].items()
        },
    }


def mapping_text(data: dict) -> str:
    lines = [
        f"H = {data['H']}",
        f"G = {data['model']}, seed = {data['seed']}",
        f"|V(H)| = {data['H_vertex_count']}, |E(H)| = {data['H_edge_count']}",
        f"|V(G)| = {data['G_vertex_count']}, |E(G)| = {data['G_edge_count']}",
        f"C++ search = no --max-depth, immersion cost = {data['cost']}",
        "",
        "Vertex mapping",
    ]
    for h_node, g_node in sorted(data["vertex_mapping"].items(), key=lambda item: int(item[0])):
        lines.append(f"  v{h_node} -> u{g_node}")
    lines.append("")
    lines.append("Edge mapping")
    for h_edge, image in sorted(data["edge_mapping"].items(), key=lambda item: int(item[0])):
        h_pair = tuple(data["H_edges"][h_edge])
        g_pairs = [tuple(edge) for edge in data["edge_mapping_as_G_edges"][h_edge]]
        lines.append(f"  e{h_edge} {h_pair} -> {image} = {g_pairs}")
    return "\n".join(lines)


def draw_python(data: dict, g_edges: list[tuple[int, int]]) -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(REPO_ROOT / ".matplotlib-cache"))

    import matplotlib

    matplotlib.use("Agg")

    import matplotlib.pyplot as plt
    import networkx as nx

    h_edges = [tuple(edge) for edge in data["H_edges"].values()]
    h_graph = nx.Graph()
    h_graph.add_nodes_from(range(data["H_vertex_count"]))
    h_graph.add_edges_from(h_edges)

    g_graph = nx.Graph()
    g_graph.add_nodes_from(range(data["G_vertex_count"]))
    g_graph.add_edges_from(g_edges)

    colors = list(plt.cm.tab10.colors[:6]) + [
        (0.92, 0.43, 0.06),
        (0.98, 0.62, 0.16),
        (0.99, 0.75, 0.30),
    ]
    h_pos = {
        0: (-1.55, 0.75),
        1: (-2.15, -0.35),
        2: (-0.95, -0.35),
        3: (-1.55, -1.20),
        4: (0.95, 0.55),
        5: (1.75, 0.55),
        6: (1.35, -0.25),
    }
    g_pos = nx.spring_layout(g_graph, seed=data["seed"], iterations=220)

    immersed_g_edges: dict[tuple[int, int], tuple[float, float, float]] = {}
    for h_edge, image in sorted(data["edge_mapping"].items(), key=lambda item: int(item[0])):
        color = colors[int(h_edge) % len(colors)]
        for g_edge_id in image:
            immersed_g_edges[tuple(g_edges[g_edge_id])] = color

    branch_vertices = {int(value) for value in data["vertex_mapping"].values()}
    fig = plt.figure(figsize=(16, 9), constrained_layout=True)
    grid = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.8, 1.25])

    h_ax = fig.add_subplot(grid[0, 0])
    h_ax.set_title("H = K4 + C3", fontsize=13)
    h_ax.axis("off")
    for edge_id, edge in enumerate(h_edges):
        nx.draw_networkx_edges(h_graph, h_pos, edgelist=[edge], edge_color=[colors[edge_id]], width=3.0, ax=h_ax)
    nx.draw_networkx_nodes(h_graph, h_pos, node_color="#f8fafc", edgecolors="#111827", linewidths=1.2, node_size=620, ax=h_ax)
    nx.draw_networkx_labels(h_graph, h_pos, labels={node: f"v{node}" for node in h_graph.nodes}, font_size=9, ax=h_ax)

    g_ax = fig.add_subplot(grid[0, 1])
    g_ax.set_title(f"G = BA(100,2), seed {data['seed']}", fontsize=13)
    g_ax.axis("off")
    background_edges = [edge for edge in g_graph.edges if tuple(sorted(edge)) not in immersed_g_edges]
    nx.draw_networkx_edges(g_graph, g_pos, edgelist=background_edges, edge_color="#cbd5e1", width=0.65, alpha=0.34, ax=g_ax)
    for edge, color in immersed_g_edges.items():
        nx.draw_networkx_edges(g_graph, g_pos, edgelist=[edge], edge_color=[color], width=2.8, ax=g_ax)
    other_vertices = [node for node in g_graph.nodes if node not in branch_vertices]
    nx.draw_networkx_nodes(g_graph, g_pos, nodelist=other_vertices, node_color="#e5e7eb", node_size=18, linewidths=0, ax=g_ax)
    nx.draw_networkx_nodes(
        g_graph,
        g_pos,
        nodelist=sorted(branch_vertices),
        node_color="#111827",
        node_size=75,
        linewidths=0,
        ax=g_ax,
    )
    nx.draw_networkx_labels(
        g_graph,
        g_pos,
        labels={node: str(node) for node in branch_vertices},
        font_size=7,
        font_color="#111827",
        verticalalignment="bottom",
        ax=g_ax,
    )

    text_ax = fig.add_subplot(grid[0, 2])
    text_ax.axis("off")
    text_ax.set_title("Explicit immersion", fontsize=13)
    text_ax.text(
        0,
        1,
        mapping_text(data),
        ha="left",
        va="top",
        family="monospace",
        fontsize=7.8,
        linespacing=1.22,
    )

    fig.savefig(OUTPUT_DIR / "k4_c3_ba100_python_drawing.png", dpi=220)
    fig.savefig(OUTPUT_DIR / "k4_c3_ba100_python_drawing.pdf")
    plt.close(fig)


def notebook_cells(data: dict, g_edges: list[tuple[int, int]]) -> list[str]:
    h_edges = guest_edges()
    input_cells = [
        "SetDirectory[DirectoryName[$InputFileName]];",
        f"hEdges = {mathematica_edge_list(h_edges, one_based=True)};",
        f"gEdges = {mathematica_edge_list(g_edges, one_based=True)};",
        f"vertexMapping = {mathematica_assoc(data['vertex_mapping'], key_shift=1, value_shift=1)};",
        f"edgeMapping = {wl_edge_mapping(data['edge_mapping'], g_edges)};",
        "edgeColorList = Join[ColorData[97] /@ Range[1, 6], {Darker[Orange, 0.05], Orange, Lighter[Orange, 0.2]}];",
        "hEdgeStyleRules = Thread[hEdges -> (Directive[#, AbsoluteThickness[3.2]] & /@ edgeColorList)];",
        """gImmersedStyleRules = Flatten[
  Table[
    Thread[edgeMapping[i] -> Directive[edgeColorList[[i]], AbsoluteThickness[2.8]]],
    {i, Length[hEdges]}
  ]
];""",
        f"""gBackgroundStyleRules = Thread[
  Complement[EdgeList[Graph[Range[{TARGET_VERTEX_COUNT}], gEdges]], Flatten[Values[edgeMapping]]] ->
    Directive[GrayLevel[0.72], Opacity[0.22], AbsoluteThickness[0.7]]
];""",
        """branchVertexStyleRules = Thread[
  Values[vertexMapping] ->
    (Directive[#, PointSize[0.018]] & /@ Join[ConstantArray[Darker[Cyan, 0.35], 4], ConstantArray[Darker[Orange, 0.15], 3]])
];""",
        """hCoordinates = Association[
  Join[
    Thread[Range[1, 4] -> (({-1.25, 0} + #) & /@ (0.72 CirclePoints[4]))],
    Thread[Range[5, 7] -> (({1.25, 0} + #) & /@ (0.62 CirclePoints[3]))]
  ]
];""",
        """hPlot = Graph[
  Range[7],
  hEdges,
  VertexCoordinates -> Normal[hCoordinates],
  VertexLabels -> Placed["Name", Center],
  EdgeStyle -> hEdgeStyleRules,
  VertexSize -> 0.22,
  ImageSize -> 300,
  PlotLabel -> Style["H = K4 + C3", 14, FontFamily -> "Arial"]
];""",
        f"""gPlot = Graph[
  Range[{TARGET_VERTEX_COUNT}],
  gEdges,
  GraphLayout -> "SpringElectricalEmbedding",
  VertexLabels -> None,
  EdgeStyle -> Join[gBackgroundStyleRules, gImmersedStyleRules],
  VertexStyle -> branchVertexStyleRules,
  VertexSize -> 0.095,
  ImageSize -> 560,
  PlotLabel -> Style["G = BA(100, 2), seed {data['seed']}", 14, FontFamily -> "Arial"]
];""",
        """mappingPanel = Pane[
  Framed[
    Column[{
      Style["Vertex mapping", Bold, 12, FontFamily -> "Arial"],
      vertexMapping,
      Spacer[8],
      Style["Edge mapping: colors match the immersed K4 and C3", Bold, 12, FontFamily -> "Arial"],
      edgeMapping
    }, Spacings -> 0.7],
    FrameStyle -> GrayLevel[0.82],
    Background -> White,
    ImageMargins -> 4
  ],
  {860, 210},
  Scrollbars -> False
];""",
        """figure = Grid[
  {{hPlot, gPlot}, {SpanFromLeft, mappingPanel}},
  Spacings -> {1.2, 0.8},
  Alignment -> Center,
  Background -> White
];""",
        """Export["k4_c3_ba100_native_colored.pdf", figure];
Export["k4_c3_ba100_native_colored.png", figure, ImageResolution -> 300];
Export["k4_c3_ba100_h_native_colored.pdf", hPlot];
Export["k4_c3_ba100_g_native_colored.pdf", gPlot];
Print["Exported native Mathematica colored figures."];""",
    ]
    cells = [
        'Cell["K4 and C3 Immersions in a Barabasi-Albert Graph", "Title"]',
        (
            'Cell["This notebook plots H = CompleteGraph[4] + CycleGraph[3] and a fixed '
            'BA(100,2) graph G natively in Mathematica. The explicit immersion mapping was '
            'computed by the C++ fhi_cli solver without --max-depth from the '
            f'BA graph with seed {data["seed"]}.", "Text"]'
        ),
    ]
    cells.extend(f'Cell[BoxData["{nb_string(code)}"], "Input"]' for code in input_cells)
    return cells


def write_notebook(data: dict, g_edges: list[tuple[int, int]]) -> None:
    notebook = (
        "Notebook[{\n"
        + ",\n".join(notebook_cells(data, g_edges))
        + '\n},\nWindowSize -> {1200, 900},\nWindowTitle -> "K4 C3 BA Immersion"]\n'
    )
    (OUTPUT_DIR / "k4_c3_ba100_native_graphs.nb").write_text(notebook, encoding="utf-8")


def write_wolfram_export_script(data: dict, g_edges: list[tuple[int, int]]) -> None:
    commands = []
    for cell in notebook_cells(data, g_edges)[2:]:
        prefix = 'Cell[BoxData["'
        suffix = '"], "Input"]'
        if cell.startswith(prefix) and cell.endswith(suffix):
            commands.append(cell[len(prefix) : -len(suffix)].encode("utf-8").decode("unicode_escape"))
    (OUTPUT_DIR / "k4_c3_ba100_native_export.wl").write_text("\n\n".join(commands) + "\n", encoding="utf-8")


def main() -> int:
    if not CLI.exists():
        print(f"C++ CLI not found at {CLI}. Run `make` in {REPO_ROOT}.")
        return 2

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    h_edges = guest_edges()
    h_path = OUTPUT_DIR / "k4_c3.hg"
    h_path.write_text(encode_hypergraph(h_edges, 7) + "\n", encoding="utf-8")

    seed = TARGET_SEED
    g_edges = ba_edges(TARGET_VERTEX_COUNT, seed)
    g_path = OUTPUT_DIR / f"ba100_m2_seed{seed}.hg"
    g_path.write_text(encode_hypergraph(g_edges, TARGET_VERTEX_COUNT, sort_edges=False) + "\n", encoding="utf-8")
    mapping = run_cpp_solver(h_path, g_path)
    if mapping is None:
        print(f"C++ solver did not find an immersion for seed {seed} within {SOLVER_TIMEOUT_SECONDS} seconds.")
        return 1

    cpp_mapping_path = OUTPUT_DIR / "k4_c3_ba100_cpp_mapping.txt"
    write_cpp_mapping_file(mapping, cpp_mapping_path)
    validate_with_cpp(h_path, g_path, cpp_mapping_path)

    data = build_data(seed, mapping, g_edges)
    (OUTPUT_DIR / "k4_c3_ba100_mapping.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "k4_c3_ba100_mapping.txt").write_text(mapping_text(data) + "\n", encoding="utf-8")
    draw_python(data, g_edges)
    write_notebook(data, g_edges)
    write_wolfram_export_script(data, g_edges)

    print(mapping_text(data))
    print("")
    print(f"Wrote {OUTPUT_DIR / 'k4_c3_ba100_native_graphs.nb'}")
    print(f"Wrote {OUTPUT_DIR / 'k4_c3_ba100_native_export.wl'}")
    print(f"Wrote {OUTPUT_DIR / 'k4_c3_ba100_python_drawing.png'}")
    print(f"Wrote {OUTPUT_DIR / 'k4_c3_ba100_python_drawing.pdf'}")
    print(f"Wrote {OUTPUT_DIR / 'k4_c3_ba100_mapping.json'}")
    print(f"Wrote {OUTPUT_DIR / 'k4_c3_ba100_mapping.txt'}")
    print(f"Wrote {cpp_mapping_path}")
    print(f"Wrote {h_path}")
    print(f"Wrote {g_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
