#!/usr/bin/env python3
"""Find and draw an immersion of K4 + K4 into a BA(50,2) graph."""

from __future__ import annotations

import itertools
import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "examples" / "output" / "k4_k4_ba"
CLI = REPO_ROOT / "build" / "fhi_cli"
TARGET_VERTEX_COUNT = 50
TARGET_M = 2
TARGET_SEED = 0
MAX_PATHS_PER_PAIR = 40


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
    first_k4 = [(u, v) for u in range(4) for v in range(u + 1, 4)]
    second_k4 = [(u, v) for u in range(4, 8) for v in range(u + 1, 8)]
    return first_k4 + second_k4


def path_edges(path: list[int]) -> set[tuple[int, int]]:
    return {tuple(sorted(edge)) for edge in zip(path, path[1:])}


def candidate_paths(graph, source: int, target: int, used_edges: set[tuple[int, int]]) -> list[list[int]]:
    import networkx as nx

    residual = graph.copy()
    residual.remove_edges_from(used_edges)
    try:
        generator = nx.shortest_simple_paths(residual, source, target)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return []

    paths: list[list[int]] = []
    try:
        for path in generator:
            if path_edges(path).isdisjoint(used_edges):
                paths.append(path)
            if len(paths) >= MAX_PATHS_PER_PAIR:
                break
    except nx.NetworkXNoPath:
        return paths
    return paths


def route_k4(graph, branch_vertices: tuple[int, int, int, int], base_used_edges: set[tuple[int, int]] | None = None):
    import networkx as nx

    used_edges = set(base_used_edges or set())
    residual = graph.copy()
    residual.remove_edges_from(used_edges)

    ordered_pairs = []
    for i, j in itertools.combinations(range(4), 2):
        try:
            distance = nx.shortest_path_length(residual, branch_vertices[i], branch_vertices[j])
        except nx.NetworkXNoPath:
            return None
        ordered_pairs.append((distance, i, j))
    pairs = [(i, j) for _, i, j in sorted(ordered_pairs, reverse=True)]

    paths: dict[tuple[int, int], list[int]] = {}

    def search(pair_index: int, current_used: set[tuple[int, int]]) -> bool:
        if pair_index == len(pairs):
            return True

        i, j = pairs[pair_index]
        options = candidate_paths(graph, branch_vertices[i], branch_vertices[j], current_used)
        options.sort(key=lambda path: (len(path), path))
        for path in options:
            edges = path_edges(path)
            if not edges.isdisjoint(current_used):
                continue
            paths[tuple(sorted((i, j)))] = path
            if search(pair_index + 1, current_used | edges):
                return True
            paths.pop(tuple(sorted((i, j))), None)
        return False

    if search(0, used_edges):
        return dict(paths)
    return None


def find_k4_k4_witness(graph):
    preferred = ((3, 0, 6, 5), (4, 9, 8, 10))
    first_paths = route_k4(graph, preferred[0])
    if first_paths is not None:
        first_used = set().union(*(path_edges(path) for path in first_paths.values()))
        second_paths = route_k4(graph, preferred[1], first_used)
        if second_paths is not None:
            return preferred[0], first_paths, preferred[1], second_paths

    residual_vertices = [vertex for vertex, degree in graph.degree() if degree >= 3]
    residual_vertices.sort(key=lambda vertex: graph.degree(vertex), reverse=True)
    for first_branch in itertools.combinations(residual_vertices, 4):
        first_paths = route_k4(graph, first_branch)
        if first_paths is None:
            continue
        first_used = set().union(*(path_edges(path) for path in first_paths.values()))
        remaining_vertices = [vertex for vertex in residual_vertices if vertex not in first_branch]
        for second_branch in itertools.combinations(remaining_vertices, 4):
            second_paths = route_k4(graph, second_branch, first_used)
            if second_paths is not None:
                return first_branch, first_paths, second_branch, second_paths
    return None


def write_encoded_inputs(h_edges: list[tuple[int, int]], g_edges: list[tuple[int, int]]) -> tuple[Path, Path]:
    h_path = OUTPUT_DIR / "k4_k4.hg"
    g_path = OUTPUT_DIR / f"ba50_m2_seed{TARGET_SEED}.hg"
    h_path.write_text(encode_hypergraph(h_edges, 8) + "\n", encoding="utf-8")
    g_path.write_text(encode_hypergraph(g_edges, TARGET_VERTEX_COUNT, sort_edges=False) + "\n", encoding="utf-8")
    return h_path, g_path


def write_cpp_mapping_file(mapping: dict, path: Path) -> None:
    node_values = [str(mapping["vertex_mapping"][str(h_node)]) for h_node in range(8)]
    edge_lines = [
        ",".join(str(edge) for edge in mapping["edge_mapping"][str(h_edge)])
        for h_edge in range(12)
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


def build_mapping(g_edges: list[tuple[int, int]], witness) -> dict:
    first_branch, first_paths, second_branch, second_paths = witness
    edge_to_id = {edge: edge_id for edge_id, edge in enumerate(g_edges)}

    vertex_mapping = {str(node): first_branch[node] for node in range(4)}
    vertex_mapping.update({str(node + 4): second_branch[node] for node in range(4)})

    edge_mapping: dict[str, list[int]] = {}
    h_edges = guest_edges()
    for edge_id, (u, v) in enumerate(h_edges):
        if edge_id < 6:
            path = first_paths[tuple(sorted((u, v)))]
        else:
            path = second_paths[tuple(sorted((u - 4, v - 4)))]
        edge_mapping[str(edge_id)] = [edge_to_id[tuple(sorted(edge))] for edge in zip(path, path[1:])]

    return {
        "cost": sum(len(image) for image in edge_mapping.values()),
        "vertex_mapping": vertex_mapping,
        "edge_mapping": edge_mapping,
    }


def serialize_mapping(mapping: dict, g_edges: list[tuple[int, int]], g_graph) -> dict:
    h_edges = guest_edges()
    return {
        "seed": TARGET_SEED,
        "model": f"BarabasiAlbertGraph[{TARGET_VERTEX_COUNT}, {TARGET_M}]",
        "H": "CompleteGraph[4] + CompleteGraph[4]",
        "H_vertex_count": 8,
        "H_edge_count": len(h_edges),
        "G_vertex_count": TARGET_VERTEX_COUNT,
        "G_edge_count": len(g_edges),
        "G_degree_sequence": sorted([degree for _, degree in g_graph.degree()], reverse=True),
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
        f"immersion cost = {data['cost']}",
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

    h_edges = [tuple(edge) for _, edge in sorted(data["H_edges"].items(), key=lambda item: int(item[0]))]
    h_graph = nx.Graph()
    h_graph.add_nodes_from(range(8))
    h_graph.add_edges_from(h_edges)

    g_graph = nx.Graph()
    g_graph.add_nodes_from(range(TARGET_VERTEX_COUNT))
    g_graph.add_edges_from(g_edges)

    colors = list(plt.cm.tab20.colors[:12])
    h_pos = {
        0: (-1.85, 0.70),
        1: (-0.95, 0.70),
        2: (-0.95, -0.20),
        3: (-1.85, -0.20),
        4: (0.95, 0.70),
        5: (1.85, 0.70),
        6: (1.85, -0.20),
        7: (0.95, -0.20),
    }
    g_pos = nx.spring_layout(g_graph, seed=TARGET_SEED, iterations=220)

    def component_image(component_edges: range) -> dict[tuple[int, int], tuple[float, float, float]]:
        image: dict[tuple[int, int], tuple[float, float, float]] = {}
        for h_edge in component_edges:
            color = colors[h_edge % len(colors)]
            for g_edge_id in data["edge_mapping"][str(h_edge)]:
                image[tuple(g_edges[g_edge_id])] = color
        return image

    first_image = component_image(range(0, 6))
    second_image = component_image(range(6, 12))
    first_branch_vertices = {int(data["vertex_mapping"][str(node)]) for node in range(4)}
    second_branch_vertices = {int(data["vertex_mapping"][str(node)]) for node in range(4, 8)}

    fig = plt.figure(figsize=(18, 10), constrained_layout=True)
    grid = fig.add_gridspec(2, 3, height_ratios=[2.2, 1.0], width_ratios=[1.0, 1.35, 1.35])

    h_ax = fig.add_subplot(grid[0, 0])
    h_ax.set_title("H = K4 + K4", fontsize=13)
    h_ax.axis("off")
    for edge_id, edge in enumerate(h_edges):
        nx.draw_networkx_edges(h_graph, h_pos, edgelist=[edge], edge_color=[colors[edge_id]], width=3.0, ax=h_ax)
    nx.draw_networkx_nodes(h_graph, h_pos, node_color="#f8fafc", edgecolors="#111827", linewidths=1.2, node_size=600, ax=h_ax)
    nx.draw_networkx_labels(h_graph, h_pos, labels={node: f"v{node}" for node in h_graph.nodes}, font_size=9, ax=h_ax)

    def draw_g_component(ax, title: str, image: dict[tuple[int, int], tuple[float, float, float]], branch_vertices: set[int]) -> None:
        ax.set_title(title, fontsize=13)
        ax.axis("off")
        background_edges = [edge for edge in g_graph.edges if tuple(sorted(edge)) not in image]
        nx.draw_networkx_edges(g_graph, g_pos, edgelist=background_edges, edge_color="#cbd5e1", width=0.8, alpha=0.30, ax=ax)
        for edge, color in image.items():
            nx.draw_networkx_edges(g_graph, g_pos, edgelist=[edge], edge_color=[color], width=3.0, ax=ax)
        other_vertices = [node for node in g_graph.nodes if node not in branch_vertices]
        nx.draw_networkx_nodes(g_graph, g_pos, nodelist=other_vertices, node_color="#e5e7eb", node_size=24, linewidths=0, ax=ax)
        nx.draw_networkx_nodes(g_graph, g_pos, nodelist=sorted(branch_vertices), node_color="#111827", node_size=95, linewidths=0, ax=ax)
        nx.draw_networkx_labels(
            g_graph,
            g_pos,
            labels={node: str(node) for node in branch_vertices},
            font_size=7,
            font_color="#111827",
            verticalalignment="bottom",
            ax=ax,
        )

    draw_g_component(fig.add_subplot(grid[0, 1]), f"G, first K4 image, seed {TARGET_SEED}", first_image, first_branch_vertices)
    draw_g_component(fig.add_subplot(grid[0, 2]), f"G, second K4 image, seed {TARGET_SEED}", second_image, second_branch_vertices)

    text_ax = fig.add_subplot(grid[1, :])
    text_ax.axis("off")
    text_ax.set_title("Explicit immersion", fontsize=13)
    text_ax.text(0, 1, mapping_text(data), ha="left", va="top", family="monospace", fontsize=7.7, linespacing=1.14)

    fig.savefig(OUTPUT_DIR / "k4_k4_ba_python_drawing.png", dpi=220)
    fig.savefig(OUTPUT_DIR / "k4_k4_ba_python_drawing.pdf")
    plt.close(fig)


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


def notebook_cells(data: dict, g_edges: list[tuple[int, int]]) -> list[str]:
    h_edges = guest_edges()
    h_coordinates = (
        "<|1 -> {-1.8, 0.65}, 2 -> {-0.95, 0.65}, 3 -> {-0.95, -0.2}, 4 -> {-1.8, -0.2}, "
        "5 -> {0.95, 0.65}, 6 -> {1.8, 0.65}, 7 -> {1.8, -0.2}, 8 -> {0.95, -0.2}|>"
    )
    input_cells = [
        "SetDirectory[DirectoryName[$InputFileName]];",
        f"hEdges = {mathematica_edge_list(h_edges, one_based=True)};",
        f"gEdges = {mathematica_edge_list(g_edges, one_based=True)};",
        f"vertexMapping = {mathematica_assoc(data['vertex_mapping'], key_shift=1, value_shift=1)};",
        f"edgeMapping = {wl_edge_mapping(data['edge_mapping'], g_edges)};",
        "edgeColorList = ColorData[97] /@ Range[Length[hEdges]];",
        "hEdgeStyleRules = Thread[hEdges -> (Directive[#, AbsoluteThickness[3.2]] & /@ edgeColorList)];",
        """edgeMappingFirst = AssociationThread[Range[1, 6], edgeMapping /@ Range[1, 6]];
edgeMappingSecond = AssociationThread[Range[7, 12], edgeMapping /@ Range[7, 12]];""",
        """gImmersedStyleRulesFirst = Flatten[
  Table[
    Thread[edgeMapping[i] -> Directive[edgeColorList[[i]], AbsoluteThickness[2.8]]],
    {i, 1, 6}
  ]
];""",
        """gImmersedStyleRulesSecond = Flatten[
  Table[
    Thread[edgeMapping[i] -> Directive[edgeColorList[[i]], AbsoluteThickness[2.8]]],
    {i, 7, 12}
  ]
];""",
        f"""gBackgroundStyleRules = Thread[
  EdgeList[Graph[Range[{TARGET_VERTEX_COUNT}], gEdges]] ->
    Directive[GrayLevel[0.72], Opacity[0.24], AbsoluteThickness[0.75]]
];""",
        """branchVertexStyleRulesFirst = Thread[Values[KeyTake[vertexMapping, Range[1, 4]]] -> Directive[Darker[Cyan, 0.35], PointSize[0.02]]];
branchVertexStyleRulesSecond = Thread[Values[KeyTake[vertexMapping, Range[5, 8]]] -> Directive[Darker[Orange, 0.15], PointSize[0.02]]];""",
        f"hCoordinates = {h_coordinates};",
        """hPlot = Graph[
  Range[8],
  hEdges,
  VertexCoordinates -> Normal[hCoordinates],
  VertexLabels -> Placed["Name", Center],
  EdgeStyle -> hEdgeStyleRules,
  VertexSize -> 0.22,
  ImageSize -> 300,
  PlotLabel -> Style["H = K4 + K4", 14, FontFamily -> "Arial"]
];""",
        f"""gPlotFirst = Graph[
  Range[{TARGET_VERTEX_COUNT}],
  gEdges,
  GraphLayout -> "SpringElectricalEmbedding",
  VertexLabels -> None,
  EdgeStyle -> Join[gBackgroundStyleRules, gImmersedStyleRulesFirst],
  VertexStyle -> branchVertexStyleRulesFirst,
  VertexSize -> 0.12,
  ImageSize -> 430,
  PlotLabel -> Style["G with first K4 image, seed {data['seed']}", 14, FontFamily -> "Arial"]
];""",
        f"""gPlotSecond = Graph[
  Range[{TARGET_VERTEX_COUNT}],
  gEdges,
  GraphLayout -> "SpringElectricalEmbedding",
  VertexLabels -> None,
  EdgeStyle -> Join[gBackgroundStyleRules, gImmersedStyleRulesSecond],
  VertexStyle -> branchVertexStyleRulesSecond,
  VertexSize -> 0.12,
  ImageSize -> 430,
  PlotLabel -> Style["G with second K4 image, seed {data['seed']}", 14, FontFamily -> "Arial"]
];""",
        """mappingPanel = Pane[
  Framed[
    Column[{
      Style["Vertex mapping", Bold, 12, FontFamily -> "Arial"],
      vertexMapping,
      Spacer[8],
      Style["Edge mapping: colors match the two immersed K4 components", Bold, 12, FontFamily -> "Arial"],
      edgeMapping
    }, Spacings -> 0.7],
    FrameStyle -> GrayLevel[0.82],
    Background -> White,
    ImageMargins -> 4
  ],
  {860, 230},
  Scrollbars -> False
];""",
        """figure = Grid[
  {{hPlot, gPlotFirst, gPlotSecond}, {SpanFromLeft, mappingPanel, SpanFromLeft}},
  Spacings -> {1.2, 0.8},
  Alignment -> Center,
  Background -> White
];""",
        """Export["k4_k4_ba_native_colored.pdf", figure];
Export["k4_k4_ba_native_colored.png", figure, ImageResolution -> 300];
Export["k4_k4_ba_h_native_colored.pdf", hPlot];
Export["k4_k4_ba_g_first_native_colored.pdf", gPlotFirst];
Export["k4_k4_ba_g_second_native_colored.pdf", gPlotSecond];
Print["Exported native Mathematica colored figures."];""",
    ]
    cells = [
        'Cell["K4 + K4 Immersion in a Barabasi-Albert Graph", "Title"]',
        (
            'Cell["This notebook plots H = CompleteGraph[4] + CompleteGraph[4] and a fixed '
            'BA(50,2) graph G natively in Mathematica. The explicit immersion mapping was '
            f'validated by the C++ fhi_cli solver from the BA graph with seed {data["seed"]}.", "Text"]'
        ),
    ]
    cells.extend(f'Cell[BoxData["{nb_string(code)}"], "Input"]' for code in input_cells)
    return cells


def write_notebook(data: dict, g_edges: list[tuple[int, int]]) -> None:
    notebook = (
        "Notebook[{\n"
        + ",\n".join(notebook_cells(data, g_edges))
        + '\n},\nWindowSize -> {1200, 900},\nWindowTitle -> "K4 K4 BA Immersion"]\n'
    )
    (OUTPUT_DIR / "k4_k4_ba_native_graphs.nb").write_text(notebook, encoding="utf-8")


def write_wolfram_export_script(data: dict, g_edges: list[tuple[int, int]]) -> None:
    commands = []
    for cell in notebook_cells(data, g_edges)[2:]:
        prefix = 'Cell[BoxData["'
        suffix = '"], "Input"]'
        if cell.startswith(prefix) and cell.endswith(suffix):
            commands.append(cell[len(prefix) : -len(suffix)].encode("utf-8").decode("unicode_escape"))
    (OUTPUT_DIR / "k4_k4_ba_native_export.wl").write_text("\n\n".join(commands) + "\n", encoding="utf-8")


def main() -> int:
    if not CLI.exists():
        print(f"C++ CLI not found at {CLI}. Run `make` in {REPO_ROOT}.")
        return 2

    sys.path.insert(0, str(REPO_ROOT))
    import networkx as nx

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    g_graph = nx.barabasi_albert_graph(TARGET_VERTEX_COUNT, TARGET_M, seed=TARGET_SEED)
    g_edges = sorted(tuple(sorted(edge)) for edge in g_graph.edges())
    witness = find_k4_k4_witness(g_graph)
    if witness is None:
        raise RuntimeError(f"no K4 + K4 immersion witness found for BA(50,2) seed {TARGET_SEED}")

    mapping = build_mapping(g_edges, witness)
    h_path, g_path = write_encoded_inputs(guest_edges(), g_edges)
    cpp_mapping_path = OUTPUT_DIR / "k4_k4_ba_cpp_mapping.txt"
    write_cpp_mapping_file(mapping, cpp_mapping_path)
    validate_with_cpp(h_path, g_path, cpp_mapping_path)

    data = serialize_mapping(mapping, g_edges, g_graph)
    text = mapping_text(data)
    (OUTPUT_DIR / "k4_k4_ba_mapping.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "k4_k4_ba_mapping.txt").write_text(text + "\n", encoding="utf-8")
    draw_python(data, g_edges)
    write_notebook(data, g_edges)
    write_wolfram_export_script(data, g_edges)

    print(text)
    print("")
    print(f"Wrote {OUTPUT_DIR / 'k4_k4_ba_mapping.json'}")
    print(f"Wrote {OUTPUT_DIR / 'k4_k4_ba_mapping.txt'}")
    print(f"Wrote {OUTPUT_DIR / 'k4_k4_ba_python_drawing.png'}")
    print(f"Wrote {OUTPUT_DIR / 'k4_k4_ba_python_drawing.pdf'}")
    print(f"Wrote {OUTPUT_DIR / 'k4_k4_ba_native_graphs.nb'}")
    print(f"Wrote {OUTPUT_DIR / 'k4_k4_ba_native_export.wl'}")
    print(f"Wrote {cpp_mapping_path}")
    print(f"Wrote {h_path}")
    print(f"Wrote {g_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
