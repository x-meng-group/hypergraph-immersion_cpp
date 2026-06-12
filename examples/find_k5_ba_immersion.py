#!/usr/bin/env python3
"""Find and draw an immersion of K5 into a BA(50, 2) graph."""

from __future__ import annotations

from pathlib import Path
import itertools
import json
import os
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(REPO_ROOT / ".matplotlib-cache"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx

from Drawing import drawing
from Hypergraph import hypergraph
from Immersion_function import immersion_function


OUTPUT_DIR = Path("examples/output/k5_ba")


def nx_graph_to_hypergraph(graph: nx.Graph) -> tuple[hypergraph, dict[int, tuple[int, int]]]:
    edges = {}
    edge_labels = {}
    for label, (u, v) in enumerate(sorted(tuple(sorted(edge)) for edge in graph.edges())):
        edges[label] = {int(u), int(v)}
        edge_labels[label] = (int(u), int(v))
    return hypergraph(set(range(graph.number_of_nodes())), edges), edge_labels


def find_example(max_seed: int = 2000):
    h_nx = nx.complete_graph(5)
    h, h_edge_labels = nx_graph_to_hypergraph(h_nx)

    for seed in range(max_seed):
        g_nx = nx.barabasi_albert_graph(50, 2, seed=seed)
        witness = find_k5_ordinary_graph_immersion(g_nx)
        if witness is None:
            continue

        branch_vertices, paths = witness
        g, g_edge_labels = nx_graph_to_hypergraph(g_nx)
        g_edge_to_label = {tuple(edge): label for label, edge in g_edge_labels.items()}

        node_mapping = {h_node: branch_vertices[h_node] for h_node in h.nodes}
        edge_mapping = {}
        for h_edge, (u, v) in h_edge_labels.items():
            path = paths[tuple(sorted((u, v)))]
            g_edge_labels_in_path = []
            for edge in zip(path, path[1:]):
                g_edge_labels_in_path.append(g_edge_to_label[tuple(sorted(edge))])
            edge_mapping[h_edge] = tuple(g_edge_labels_in_path)

        alpha = immersion_function(node_mapping, edge_mapping, g, h)
        if not alpha.is_immersion():
            raise RuntimeError("ordinary graph witness did not convert to a valid immersion")
        return seed, h, g, alpha, h_edge_labels, g_edge_labels, g_nx
    raise RuntimeError(f"no K5 immersion found in BA(50,2) seeds 0..{max_seed - 1}")


def find_k5_ordinary_graph_immersion(graph: nx.Graph):
    """Return branch vertices and edge-disjoint paths for a K5 immersion."""

    high_degree_vertices = [vertex for vertex, degree in graph.degree() if degree >= 4]
    for branch_vertices in itertools.combinations(high_degree_vertices, 5):
        pair_order = []
        feasible = True
        for i, j in itertools.combinations(range(5), 2):
            try:
                path = nx.shortest_path(graph, branch_vertices[i], branch_vertices[j])
            except nx.NetworkXNoPath:
                feasible = False
                break
            pair_order.append((len(path), i, j))
        if not feasible:
            continue

        used_edges = set()
        paths = {}
        for _, i, j in sorted(pair_order, reverse=True):
            residual = graph.copy()
            residual.remove_edges_from(used_edges)
            try:
                path = nx.shortest_path(residual, branch_vertices[i], branch_vertices[j])
            except nx.NetworkXNoPath:
                feasible = False
                break
            path_edges = {tuple(sorted(edge)) for edge in zip(path, path[1:])}
            if used_edges & path_edges:
                feasible = False
                break
            used_edges |= path_edges
            paths[tuple(sorted((i, j)))] = path

        if feasible:
            return tuple(branch_vertices), paths

    return None


def serialize_mapping(seed, h, g, alpha, h_edge_labels, g_edge_labels, g_nx):
    vertex_mapping = {str(node): alpha.evaluate("node", node) for node in sorted(h.nodes)}
    edge_mapping = {}
    edge_mapping_as_graph_edges = {}
    for edge in sorted(h.hyperedges):
        image = list(alpha.evaluate("edge", edge))
        edge_mapping[str(edge)] = image
        edge_mapping_as_graph_edges[str(edge)] = [g_edge_labels[g_edge] for g_edge in image]

    return {
        "seed": seed,
        "model": "BarabasiAlbertGraph[50, 2]",
        "H": "CompleteGraph[5]",
        "H_vertex_count": h.node_count,
        "H_edge_count": h.hyperedge_count,
        "G_vertex_count": g.node_count,
        "G_edge_count": g.hyperedge_count,
        "G_degree_sequence": sorted([degree for _, degree in g_nx.degree()], reverse=True),
        "vertex_mapping": vertex_mapping,
        "H_edges": {str(edge): h_edge_labels[edge] for edge in sorted(h_edge_labels)},
        "edge_mapping": edge_mapping,
        "edge_mapping_as_G_edges": edge_mapping_as_graph_edges,
    }


def mapping_text(data) -> str:
    lines = [
        f"H = {data['H']}",
        f"G = {data['model']}, seed = {data['seed']}",
        f"|V(H)| = {data['H_vertex_count']}, |E(H)| = {data['H_edge_count']}",
        f"|V(G)| = {data['G_vertex_count']}, |E(G)| = {data['G_edge_count']}",
        "",
        "Vertex mapping",
    ]
    for h_node, g_node in data["vertex_mapping"].items():
        lines.append(f"  v{h_node} -> u{g_node}")
    lines.append("")
    lines.append("Edge mapping")
    for h_edge, image in data["edge_mapping"].items():
        graph_edges = data["edge_mapping_as_G_edges"][h_edge]
        lines.append(f"  e{h_edge} {tuple(data['H_edges'][h_edge])} -> {image} = {graph_edges}")
    return "\n".join(lines)


def draw_python(alpha, text: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(14, 9), constrained_layout=True)
    ax = fig.add_subplot(1, 2, 1)
    ax.set_title("K5 immersed in BA(50,2)", fontsize=13)
    ax.axis("off")
    ax.set_aspect("equal", adjustable="box")
    plt.sca(ax)
    diagram = drawing.line_draw_immersion(
        alpha,
        saturation=0.72,
        width=9,
        node_radius=0.12,
        node_opacity=0.78,
        node_color=(0.33, 0.22, 0.68),
        edge_opacity=0.42,
        arrow_thickness=0.04,
        arrowhead_length=0.09,
        arrowhead_width=0.12,
        hyperedge_fill_radius=0.05,
        match_colors=True,
    )
    x_min, y_min, x_max, y_max = diagram.bounds()
    ax.set_xlim(x_min - 1.2, x_max + 1.2)
    ax.set_ylim(y_min - 1.0, y_max + 1.0)
    diagram.plot(resolution=70)
    ax.text(-4.5, y_max + 0.4, "H = K5", ha="center", va="bottom", fontsize=11, weight="bold")
    ax.text(4.5, y_max + 0.4, "G = BA(50,2)", ha="center", va="bottom", fontsize=11, weight="bold")

    text_ax = fig.add_subplot(1, 2, 2)
    text_ax.axis("off")
    text_ax.set_title("Explicit immersion", fontsize=13)
    text_ax.text(0, 1, text, ha="left", va="top", family="monospace", fontsize=8.5, linespacing=1.25)
    fig.savefig(OUTPUT_DIR / "k5_ba_python_drawing.png", dpi=220)
    fig.savefig(OUTPUT_DIR / "k5_ba_python_drawing.pdf")
    plt.close(fig)


def mathematica_edge_list(graph: nx.Graph) -> str:
    edges = sorted(tuple(sorted(edge)) for edge in graph.edges())
    return "{" + ", ".join(f"{u} \\[UndirectedEdge] {v}" for u, v in edges) + "}"


def mathematica_assoc(mapping: dict) -> str:
    entries = []
    for key, value in mapping.items():
        if isinstance(value, list):
            value_string = "{" + ", ".join(str(item) for item in value) + "}"
        else:
            value_string = str(value)
        entries.append(f"{key} -> {value_string}")
    return "<|" + ", ".join(entries) + "|>"


def write_mathematica_notebook(data, g_nx: nx.Graph) -> None:
    """Write a real .nb file with native Mathematica graph plotting cells."""

    g_edges = mathematica_edge_list(nx.relabel_nodes(g_nx, lambda x: x + 1))
    branch_vertices = {int(h_node) + 1: int(g_node) + 1 for h_node, g_node in data["vertex_mapping"].items()}
    edge_mapping = {}
    for h_edge, paths in data["edge_mapping_as_G_edges"].items():
        edge_mapping[int(h_edge) + 1] = [tuple(x + 1 for x in edge) for edge in paths]

    edge_mapping_entries = []
    for h_edge, path_edges in edge_mapping.items():
        rhs = "{" + ", ".join(f"{u} \\[UndirectedEdge] {v}" for u, v in path_edges) + "}"
        edge_mapping_entries.append(f"{h_edge} -> {rhs}")
    edge_mapping_wl = "<|" + ", ".join(edge_mapping_entries) + "|>"
    h_edge_entries = []
    for h_edge in sorted(data["H_edges"], key=lambda key: int(key)):
        u, v = data["H_edges"][h_edge]
        h_edge_entries.append(f"{u + 1} \\[UndirectedEdge] {v + 1}")
    h_edges_wl = "{" + ", ".join(h_edge_entries) + "}"

    def nb_string(text: str) -> str:
        return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

    input_cells = [
        "h = CompleteGraph[5];",
        'gFresh = RandomGraph[BarabasiAlbertGraphDistribution[50, 2], VertexLabels -> "Name"];',
        f"gEdges = {g_edges};",
        'g = Graph[Range[50], gEdges, VertexLabels -> "Name", GraphLayout -> "SpringElectricalEmbedding"];',
        f"vertexMapping = {mathematica_assoc(branch_vertices)};",
        f"hEdges = {h_edges_wl};",
        f"edgeMapping = {edge_mapping_wl};",
        'edgeColorList = ColorData[97] /@ Range[Length[hEdges]];',
        'hEdgeStyleRules = Thread[hEdges -> edgeColorList];',
        'gEdgeStyleRules = Flatten[Table[Thread[edgeMapping[i] -> edgeColorList[[i]]], {i, Length[hEdges]}]];',
        'branchVertexStyleRules = Thread[Values[vertexMapping] -> Black];',
        'Row[{Graph[h, VertexLabels -> "Name", EdgeStyle -> hEdgeStyleRules, ImageSize -> 300], Spacer[20], Graph[g, EdgeStyle -> gEdgeStyleRules, VertexStyle -> branchVertexStyleRules, ImageSize -> 550]}]',
        'Column[{"Vertex mapping", vertexMapping, "Edge mapping", edgeMapping}]',
        'Graph[g, EdgeStyle -> Join[gEdgeStyleRules, Thread[Complement[EdgeList[g], Flatten[Values[edgeMapping]]] -> Directive[Gray, Opacity[0.2]]]], VertexStyle -> branchVertexStyleRules, ImageSize -> 700]',
    ]
    cells = [
        'Cell["K5 Immersion in a Barabasi-Albert Graph", "Title"]',
        f'Cell["This notebook plots H = CompleteGraph[5] and a fixed BA(50,2) graph G natively in Mathematica. The explicit G edge list is included because this environment could not run an activated local Wolfram kernel. The graph was found from a Barabasi-Albert process with seed {data["seed"]}.", "Text"]',
    ]
    for code in input_cells:
        cells.append(f'Cell[BoxData["{nb_string(code)}"], "Input"]')

    nb = "Notebook[{\n" + ",\n".join(cells) + '\n},\nWindowSize -> {1200, 900},\nWindowTitle -> "K5 BA Immersion"]\n'
    (OUTPUT_DIR / "k5_ba_native_graphs.nb").write_text(nb, encoding="utf-8")


def write_wolfram_export_script(data, g_nx: nx.Graph) -> None:
    """Write a Wolfram Language script that exports color-matched native figures."""

    g_edges = mathematica_edge_list(nx.relabel_nodes(g_nx, lambda x: x + 1))
    h_edge_entries = []
    for h_edge in sorted(data["H_edges"], key=lambda key: int(key)):
        u, v = data["H_edges"][h_edge]
        h_edge_entries.append(f"{u + 1} \\[UndirectedEdge] {v + 1}")
    h_edges_wl = "{" + ", ".join(h_edge_entries) + "}"

    branch_vertices = {int(h_node) + 1: int(g_node) + 1 for h_node, g_node in data["vertex_mapping"].items()}

    edge_mapping_entries = []
    for h_edge, paths in data["edge_mapping_as_G_edges"].items():
        path_edges = [tuple(x + 1 for x in edge) for edge in paths]
        rhs = "{" + ", ".join(f"{u} \\[UndirectedEdge] {v}" for u, v in path_edges) + "}"
        edge_mapping_entries.append(f"{int(h_edge) + 1} -> {rhs}")
    edge_mapping_wl = "<|" + ", ".join(edge_mapping_entries) + "|>"

    script = """
SetDirectory[DirectoryName[$InputFileName]];

hEdges = __H_EDGES__;
gEdges = __G_EDGES__;
vertexMapping = __VERTEX_MAPPING__;
edgeMapping = __EDGE_MAPPING__;

edgeColorList = ColorData[97] /@ Range[Length[hEdges]];
hEdgeStyleRules = Thread[hEdges -> (Directive[#, AbsoluteThickness[3.2]] & /@ edgeColorList)];
gImmersedStyleRules = Flatten[
  Table[
    Thread[edgeMapping[i] -> Directive[edgeColorList[[i]], AbsoluteThickness[2.6]]],
    {i, Length[hEdges]}
  ]
];
gBackgroundStyleRules = Thread[
  Complement[EdgeList[Graph[Range[50], gEdges]], Flatten[Values[edgeMapping]]] ->
    Directive[GrayLevel[0.72], Opacity[0.24], AbsoluteThickness[0.7]]
];
branchVertexStyleRules = Thread[Values[vertexMapping] -> Directive[Black, PointSize[0.018]]];

hPlot = Graph[
  Range[5],
  hEdges,
  VertexLabels -> Placed["Name", Center],
  GraphLayout -> "CircularEmbedding",
  EdgeStyle -> hEdgeStyleRules,
  VertexSize -> 0.22,
  ImageSize -> 260,
  PlotLabel -> Style["H = K5", 14, FontFamily -> "Arial"]
];

gPlot = Graph[
  Range[50],
  gEdges,
  GraphLayout -> "SpringElectricalEmbedding",
  VertexLabels -> None,
  EdgeStyle -> Join[gBackgroundStyleRules, gImmersedStyleRules],
  VertexStyle -> branchVertexStyleRules,
  VertexSize -> 0.11,
  ImageSize -> 540,
  PlotLabel -> Style["G = BA(50, 2), seed 0", 14, FontFamily -> "Arial"]
];

mappingPanel = Pane[
  Framed[
    Column[{
    Style["Vertex mapping", Bold, 12, FontFamily -> "Arial"],
    vertexMapping,
    Spacer[8],
    Style["Edge mapping: each K5 color matches its immersed path", Bold, 12, FontFamily -> "Arial"],
    edgeMapping
    }, Spacings -> 0.7],
    FrameStyle -> GrayLevel[0.82],
    Background -> White,
    ImageMargins -> 4
  ],
  {820, 190},
  Scrollbars -> False
];

figure = Grid[
  {{hPlot, gPlot}, {SpanFromLeft, mappingPanel}},
  Spacings -> {1.2, 0.8},
  Alignment -> Center,
  Background -> White
];

Export["k5_ba_native_colored.pdf", figure];
Export["k5_ba_native_colored.png", figure, ImageResolution -> 300];
Export["k5_ba_h_native_colored.pdf", hPlot];
Export["k5_ba_g_native_colored.pdf", gPlot];

Print["Exported native Mathematica colored figures."];
"""
    script = (
        script.replace("__H_EDGES__", h_edges_wl)
        .replace("__G_EDGES__", g_edges)
        .replace("__VERTEX_MAPPING__", mathematica_assoc(branch_vertices))
        .replace("__EDGE_MAPPING__", edge_mapping_wl)
    )
    (OUTPUT_DIR / "k5_ba_native_export.wl").write_text(script.strip() + "\n", encoding="utf-8")


def main() -> int:
    seed, h, g, alpha, h_edge_labels, g_edge_labels, g_nx = find_example()
    data = serialize_mapping(seed, h, g, alpha, h_edge_labels, g_edge_labels, g_nx)
    text = mapping_text(data)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "k5_ba_mapping.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "k5_ba_mapping.txt").write_text(text + "\n", encoding="utf-8")
    draw_python(alpha, text)
    write_mathematica_notebook(data, g_nx)
    write_wolfram_export_script(data, g_nx)
    print(text)
    print("")
    print(f"Wrote {OUTPUT_DIR / 'k5_ba_mapping.json'}")
    print(f"Wrote {OUTPUT_DIR / 'k5_ba_mapping.txt'}")
    print(f"Wrote {OUTPUT_DIR / 'k5_ba_python_drawing.png'}")
    print(f"Wrote {OUTPUT_DIR / 'k5_ba_python_drawing.pdf'}")
    print(f"Wrote {OUTPUT_DIR / 'k5_ba_native_graphs.nb'}")
    print(f"Wrote {OUTPUT_DIR / 'k5_ba_native_export.wl'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
