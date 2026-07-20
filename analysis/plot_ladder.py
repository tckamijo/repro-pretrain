#!/usr/bin/env python3
"""analysis/plot_ladder.py — publication figures for the SEALED size-ladder results.

Reads runs/ladder_*.json (via analyze_ladder helpers) and writes 600 dpi figures:
  fig_h1_scale_emergence.png : cross-backend prediction disagreement vs step,
      10m (CUDA<->CPU) stays ~0 while 50m (CUDA<->MPS) emerges -> scale emergence.
      Inset/bar: final-step disagreement by size with 3-seed error bars.
  fig_h3_precision.png       : 50m CUDA fp32<->{bf16,fp16} disagreement vs step,
      with the 50m fp32 cross-backend (CUDA<->MPS) as reference.

Deterministic, no network. Byte-level prediction disagreement = % of the 4096
fixed-val argmax positions that differ between two runs at a given snapshot step.
"""
import os
import sys
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_ladder import load_runs, backends_at, pair_disagreement, final_step, ROOT

RUNS = os.path.join(ROOT, "runs", "ladder_*.json")
OUT = os.path.dirname(os.path.abspath(__file__))
MILES = [50, 100, 200, 400, 800, 1600, 3200, 4000]


def curve(rA, rB):
    steps = sorted(set(rA["snaps"]) & set(rB["snaps"]))
    return steps, [pair_disagreement(rA, rB, s) for s in steps]


def fig_h1(runs):
    SIZES = ["10m", "30m", "50m", "75m"]
    fig, (ax, axb) = plt.subplots(1, 2, figsize=(11, 4.4),
                                  gridspec_kw={"width_ratios": [1.15, 1]})
    cols = {"10m": "#3a7ca5", "30m": "#e08a1e", "50m": "#d1495b", "75m": "#7b1e3a"}

    # left: 4-point CUDA<->MPS scale curve (params vs 3-seed disagreement)
    xs, means, errs, out = [], [], [], []
    for size in SIZES:
        be = backends_at(runs, size)
        if "honmaru-cuda" not in be or "mac-mps" not in be:
            continue
        vs = [pair_disagreement(be["honmaru-cuda"][s], be["mac-mps"][s])
              for s in sorted(set(be["honmaru-cuda"]) & set(be["mac-mps"]))]
        vs = [v for v in vs if v is not None]
        p_ = be["honmaru-cuda"][0]["n_params"] / 1e6
        m_ = statistics.mean(vs); e_ = statistics.pstdev(vs) if len(vs) > 1 else 0
        xs.append(p_); means.append(m_); errs.append(e_); out.append((size, p_, m_, e_))
    ax.errorbar(xs, means, yerr=errs, fmt="o-", color="#d1495b", lw=2, capsize=4, ms=7)
    ax.axhline(10, ls="--", color="gray", lw=1)
    ax.text(xs[-1], 10.5, "10% band", color="gray", fontsize=8, ha="right")
    for x, m in zip(xs, means):
        ax.annotate(f"{m:.1f}%", (x, m), textcoords="offset points",
                    xytext=(0, 9), ha="center", fontsize=9)
    ax.set_xlabel("model size (M parameters)")
    ax.set_ylabel("CUDA↔MPS prediction disagreement (%)")
    ax.set_title("Divergence emerges with scale, then saturates")
    ax.set_ylim(-1, 16.5); ax.grid(alpha=0.25)

    # right: per-step onset curves (seed 0) for the 4 sizes
    for size in SIZES:
        be = backends_at(runs, size)
        if "honmaru-cuda" not in be or "mac-mps" not in be:
            continue
        s, c = curve(be["honmaru-cuda"][0], be["mac-mps"][0])
        pm = be["honmaru-cuda"][0]["n_params"] / 1e6
        axb.plot(s, c, "o-", color=cols[size], lw=1.8, ms=4, label=f"{pm:.0f}M")
    axb.set_xlabel("training step"); axb.set_ylabel("prediction disagreement (%)")
    axb.set_title("CUDA↔MPS onset vs step (seed 0)")
    axb.legend(frameon=False, fontsize=8, title="params"); axb.grid(alpha=0.25)
    fig.tight_layout()
    p = os.path.join(OUT, "fig_h1_scale_emergence.png")
    fig.savefig(p, dpi=600); plt.close(fig)
    return p, out


def fig_h3(runs):
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ref = runs[("50m", "honmaru-cuda", "fp32", 0, False)]
    pairs = [("bf16", "#e08a1e", "fp32↔bf16"),
             ("fp16", "#8b0000", "fp32↔fp16")]
    for dtype, col, lab in pairs:
        r = runs.get(("50m", "honmaru-cuda", dtype, 0, False))
        if not r:
            continue
        s, c = curve(ref, r)
        ax.plot(s, c, "o-", color=col, lw=2, label=lab)
    # reference: fp32 cross-backend (CUDA<->MPS) at 50m
    be50 = backends_at(runs, "50m")
    s, c = curve(be50["honmaru-cuda"][0], be50["mac-mps"][0])
    ax.plot(s, c, "s--", color="#3a7ca5", lw=1.6, label="fp32 CUDA↔MPS (ref)")
    ax.set_xlabel("training step"); ax.set_ylabel("prediction disagreement (%)")
    ax.set_title("Low precision brings divergence onset earlier (50M CUDA)")
    ax.legend(frameon=False); ax.grid(alpha=0.25)
    fig.tight_layout()
    p = os.path.join(OUT, "fig_h3_precision.png")
    fig.savefig(p, dpi=600); plt.close(fig)
    return p


def main():
    runs = load_runs(RUNS)
    p1, curve4 = fig_h1(runs)
    p2 = fig_h3(runs)
    pts = "  ".join(f"{s.upper()}({pm:.0f}M) {m:.1f}±{e:.1f}%" for s, pm, m, e in curve4)
    print(f"[fig] {p1}\n       CUDA<->MPS scale curve: {pts}")
    print(f"[fig] {p2}")


if __name__ == "__main__":
    main()
