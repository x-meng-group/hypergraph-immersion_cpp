#!/usr/bin/env python3
"""Draw a smaller explicit hypergraph immersion example."""

from __future__ import annotations

from pathlib import Path
import os
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(REPO_ROOT / ".matplotlib-cache"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from Drawing import drawing
from Hypergraph import hypergraph
from Immersion_function import immersion_function


OUTPUT_DIR = Path("examples/output")


def build_example() -> tuple[hypergraph, hypergraph, immersion_function]:
    # H has exactly five vertices and three hyperedges.
    h_edges = {
        0: {0, 1, 2},
        1: {2, 3},
        2: {1, 3, 4},
    }
    h = hypergraph(set(range(5)), h_edges)

    # G has exactly ten vertices and six hyperedges. The first five target
    # hyperedges participate in the immersion; F5 is background structure.
    g_edges = {
        # alpha(E0), covering alpha(v0)=u0, alpha(v1)=u2, alpha(v2)=u4
        0: {0, 2, 3},
        1: {3, 4, 5},
        # alpha(E1), covering alpha(v2)=u4, alpha(v3)=u6
        2: {4, 6, 7},
        # alpha(E2), covering alpha(v1)=u2, alpha(v3)=u6, alpha(v4)=u8
        3: {2, 6, 9},
        4: {8, 9},
        # Background G-only hyperedge.
        5: {1, 5, 7},
    }
    g = hypergraph(set(range(10)), g_edges)

    node_mapping = {
        0: 0,
        1: 2,
        2: 4,
        3: 6,
        4: 8,
    }
    edge_mapping = {
        0: (0, 1),
        1: (2,),
        2: (3, 4),
    }

    alpha = immersion_function(node_mapping, edge_mapping, g, h)
    if not alpha.is_immersion():
        raise RuntimeError("constructed small example is not a valid immersion")
    return h, g, alpha


def mapping_text(h: hypergraph, g: hypergraph, alpha: immersion_function) -> str:
    lines = ["Vertex mapping"]
    for node in sorted(h.nodes):
        lines.append(f"  v{node} -> u{alpha.evaluate('node', node)}")
    lines.append("")
    lines.append("Edge mapping")
    for edge in sorted(h.hyperedges):
        g_edges = ", ".join(f"F{g_edge}" for g_edge in alpha.evaluate("edge", edge))
        lines.append(f"  E{edge} {sorted(h.hyperedge_sets[edge])} -> {{{g_edges}}}")
    lines.append("")
    lines.append("Target G summary")
    lines.append(f"  |V(H)| = {h.node_count}, |E(H)| = {h.hyperedge_count}")
    lines.append(f"  |V(G)| = {g.node_count}, |E(G)| = {g.hyperedge_count}")
    lines.append("  Immersed G edges: F0-F4")
    lines.append("  Background G-only edge: F5")
    return "\n".join(lines)


def draw(alpha: immersion_function, text: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(11, 6), constrained_layout=True)
    ax = fig.add_subplot(1, 2, 1)
    ax.set_title("Small immersion of H into G", fontsize=12)
    ax.axis("off")
    ax.set_aspect("equal", adjustable="box")
    plt.sca(ax)

    diagram = drawing.line_draw_immersion(
        alpha,
        saturation=0.72,
        width=6,
        node_radius=0.18,
        node_opacity=0.82,
        node_color=(0.33, 0.22, 0.68),
        edge_opacity=0.5,
        arrow_thickness=0.05,
        arrowhead_length=0.12,
        arrowhead_width=0.15,
        hyperedge_fill_radius=0.1,
        match_colors=True,
    )
    x_min, y_min, x_max, y_max = diagram.bounds()
    ax.set_xlim(x_min - 1.0, x_max + 1.0)
    ax.set_ylim(y_min - 0.8, y_max + 0.8)
    diagram.plot(resolution=80)
    ax.text(-3, y_max + 0.3, "H", ha="center", va="bottom", fontsize=11, weight="bold")
    ax.text(3, y_max + 0.3, "G", ha="center", va="bottom", fontsize=11, weight="bold")

    text_ax = fig.add_subplot(1, 2, 2)
    text_ax.axis("off")
    text_ax.set_title("Explicit maps", fontsize=12)
    text_ax.text(
        0.0,
        1.0,
        text,
        ha="left",
        va="top",
        family="monospace",
        fontsize=10,
        linespacing=1.35,
    )

    png_path = OUTPUT_DIR / "small_immersion.png"
    pdf_path = OUTPUT_DIR / "small_immersion.pdf"
    fig.savefig(png_path, dpi=220)
    fig.savefig(pdf_path)
    plt.close(fig)


def main() -> int:
    h, g, alpha = build_example()
    text = mapping_text(h, g, alpha)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "small_immersion_mapping.txt").write_text(text + "\n", encoding="utf-8")
    draw(alpha, text)
    print(text)
    print("")
    print(f"Wrote {OUTPUT_DIR / 'small_immersion.png'}")
    print(f"Wrote {OUTPUT_DIR / 'small_immersion.pdf'}")
    print(f"Wrote {OUTPUT_DIR / 'small_immersion_mapping.txt'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
