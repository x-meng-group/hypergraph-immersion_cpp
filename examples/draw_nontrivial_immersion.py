#!/usr/bin/env python3
"""Draw a nontrivial hypergraph immersion using the original drawing utilities."""

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
    # Pattern hypergraph H.
    h_edges = {
        0: {0, 1, 2},
        1: {2, 3},
        2: {1, 3, 4},
        3: {0, 4},
    }
    h = hypergraph(set(range(5)), h_edges)

    # Target hypergraph G. It has 32 vertices and 21 hyperedges; only the first
    # 12 target hyperedges participate in the immersion, the rest are background.
    g_edges = {
        # alpha(E0): connected chain covering alpha(0), alpha(1), alpha(2)
        0: {3, 5, 6},
        1: {6, 9, 10},
        2: {10, 14, 15},
        # alpha(E1): connected pair covering alpha(2), alpha(3)
        3: {14, 16, 17},
        4: {17, 21, 22},
        # alpha(E2): connected patch covering alpha(1), alpha(3), alpha(4)
        5: {9, 18, 19},
        6: {19, 21, 23},
        7: {23, 25, 28},
        8: {18, 25, 29},
        # alpha(E3): connected triangle-like path covering alpha(0), alpha(4)
        9: {3, 30, 31},
        10: {31, 27, 28},
        11: {3, 26, 27},
        # Extra G-only structure.
        12: {0, 1, 2},
        13: {2, 4, 6},
        14: {4, 7, 8},
        15: {8, 11, 12},
        16: {12, 13, 15},
        17: {15, 20, 24},
        18: {20, 24, 29},
        19: {1, 11, 22},
        20: {0, 13, 30},
    }
    g = hypergraph(set(range(32)), g_edges)

    node_mapping = {
        0: 3,
        1: 9,
        2: 14,
        3: 21,
        4: 28,
    }
    edge_mapping = {
        0: (0, 1, 2),
        1: (3, 4),
        2: (5, 6, 7, 8),
        3: (9, 10, 11),
    }

    alpha = immersion_function(node_mapping, edge_mapping, g, h)
    if not alpha.is_immersion():
        raise RuntimeError("constructed example is not a valid immersion")
    return h, g, alpha


def mapping_text(h: hypergraph, g: hypergraph, alpha: immersion_function) -> str:
    lines = []
    lines.append("Vertex mapping")
    for node in sorted(h.nodes):
        lines.append(f"  v{node} -> u{alpha.evaluate('node', node)}")
    lines.append("")
    lines.append("Edge mapping")
    for edge in sorted(h.hyperedges):
        g_edges = ", ".join(f"F{g_edge}" for g_edge in alpha.evaluate("edge", edge))
        lines.append(f"  E{edge} {sorted(h.hyperedge_sets[edge])} -> {{{g_edges}}}")
    lines.append("")
    lines.append("Target G summary")
    lines.append(f"  |V(G)| = {g.node_count}, |E(G)| = {g.hyperedge_count}")
    lines.append("  Immersed G edges: F0-F11")
    lines.append("  Background G-only edges: F12-F20")
    return "\n".join(lines)


def draw(alpha: immersion_function, text: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(13, 9), constrained_layout=True)
    ax = fig.add_subplot(1, 2, 1)
    ax.set_title("Immersion of H into G", fontsize=13)
    ax.axis("off")
    ax.set_aspect("equal", adjustable="box")
    plt.sca(ax)

    diagram = drawing.line_draw_immersion(
        alpha,
        saturation=0.72,
        width=8,
        node_radius=0.16,
        node_opacity=0.78,
        node_color=(0.33, 0.22, 0.68),
        edge_opacity=0.48,
        arrow_thickness=0.055,
        arrowhead_length=0.12,
        arrowhead_width=0.15,
        hyperedge_fill_radius=0.08,
        match_colors=True,
    )
    x_min, y_min, x_max, y_max = diagram.bounds()
    ax.set_xlim(x_min - 1.2, x_max + 1.2)
    ax.set_ylim(y_min - 1.0, y_max + 1.0)
    diagram.plot(resolution=80)
    ax.text(-4, y_max + 0.45, "H", ha="center", va="bottom", fontsize=12, weight="bold")
    ax.text(4, y_max + 0.45, "G", ha="center", va="bottom", fontsize=12, weight="bold")

    text_ax = fig.add_subplot(1, 2, 2)
    text_ax.axis("off")
    text_ax.set_title("Explicit immersion maps", fontsize=13)
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

    png_path = OUTPUT_DIR / "nontrivial_immersion.png"
    pdf_path = OUTPUT_DIR / "nontrivial_immersion.pdf"
    fig.savefig(png_path, dpi=220)
    fig.savefig(pdf_path)
    plt.close(fig)


def main() -> int:
    h, g, alpha = build_example()
    text = mapping_text(h, g, alpha)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "nontrivial_immersion_mapping.txt").write_text(text + "\n", encoding="utf-8")
    draw(alpha, text)
    print(text)
    print("")
    print(f"Wrote {OUTPUT_DIR / 'nontrivial_immersion.png'}")
    print(f"Wrote {OUTPUT_DIR / 'nontrivial_immersion.pdf'}")
    print(f"Wrote {OUTPUT_DIR / 'nontrivial_immersion_mapping.txt'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
