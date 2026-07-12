#!/usr/bin/env python3
"""analysis/fig_abstract_schematic.py — graphical-abstract schematic for the finding.

Block-and-arrow "so what" figure (matplotlib, paper-safe, no external assets):
  ONE RECIPE (same seed/data/code) -> {CPU, CUDA, MPS}
   left  panel: small model (10M) -> backends CONVERGE to ~one model (0.2%)  [OK]
   right panel: large model (50M) -> backends DIVERGE to different models (13%, equal loss) [X]
Numbers come from the SEALED analysis (analysis/ladder_report.md). Labels are exact.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = os.path.dirname(os.path.abspath(__file__))
BLUE, RED, INK, GRAY = "#3a7ca5", "#d1495b", "#22303a", "#8a8a8a"
CHIP = "#eef3f6"


def box(ax, x, y, w, h, text, fc, ec=INK, fs=11, bold=False):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                 boxstyle="round,pad=0.02,rounding_size=0.06",
                 linewidth=1.4, edgecolor=ec, facecolor=fc, zorder=2))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=INK,
            fontweight="bold" if bold else "normal", zorder=3)


def arrow(ax, x1, y1, x2, y2, color=INK, lw=1.6):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                 mutation_scale=14, linewidth=lw, color=color, zorder=1))


def panel(ax, title, outcome_diverges):
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    ax.set_title(title, fontsize=12.5, fontweight="bold", pad=6)
    # recipe
    box(ax, 5, 9.1, 7.4, 1.15,
        "ONE RECIPE\nsame seed · same data · same code", "#f4efe6", fs=10)
    # three backends
    xs = [2.2, 5.0, 7.8]
    for x, name in zip(xs, ["CPU", "CUDA", "MPS"]):
        arrow(ax, 5, 8.5, x, 6.9)
        box(ax, x, 6.35, 1.7, 1.0, name, CHIP, fs=11, bold=True)
    if not outcome_diverges:
        # converge to one model
        for x in xs:
            arrow(ax, x, 5.85, 5, 3.9, color=GRAY)
        box(ax, 5, 3.25, 5.2, 1.25, "≈ ONE model", "#e5f0e8", ec=BLUE, fs=12, bold=True)
        ax.text(5, 1.7, "backends agree\n0.2% predictions differ  ✓",
                ha="center", va="center", fontsize=11, color=BLUE, fontweight="bold")
    else:
        # diverge to three models
        labels = ["model A", "model B", "model C"]
        for x, lab in zip(xs, labels):
            arrow(ax, x, 5.85, x, 4.2, color=RED)
            box(ax, x, 3.6, 1.9, 1.05, lab, "#f7e4e7", ec=RED, fs=10.5, bold=True)
        ax.text(5, 1.7, "backends disagree\n13% predictions differ — yet equal loss  ✗",
                ha="center", va="center", fontsize=11, color=RED, fontweight="bold")


def main():
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11, 5.4))
    panel(axL, "Small model (10M params)", outcome_diverges=False)
    panel(axR, "Large model (50M params)", outcome_diverges=True)
    fig.suptitle("Hardware reproducibility of pretraining breaks down with scale",
                 fontsize=14.5, fontweight="bold", y=0.99)
    fig.text(0.5, 0.015,
             "Same recipe on CPU / CUDA / MPS: identical at small scale, "
             "divergent 'equally-good-but-different' models at large scale.",
             ha="center", fontsize=9.5, color=GRAY)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    p = os.path.join(OUT, "fig_abstract_schematic.png")
    fig.savefig(p, dpi=600); plt.close(fig)
    print(f"[fig] {p}")


if __name__ == "__main__":
    main()
