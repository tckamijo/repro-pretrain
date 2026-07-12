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
    fig, (ax, axb) = plt.subplots(1, 2, figsize=(10, 4.2),
                                  gridspec_kw={"width_ratios": [2.2, 1]})
    # per-step curves: 10m CUDA<->CPU (s0), 50m CUDA<->MPS (s0)
    be10 = backends_at(runs, "10m")
    be50 = backends_at(runs, "50m")
    s10, c10 = curve(be10["honmaru-cuda"][0], be10["honmaru-cpu"][0])
    s50, c50 = curve(be50["honmaru-cuda"][0], be50["mac-mps"][0])
    ax.plot(s10, c10, "o-", color="#3a7ca5", lw=2, label="10M  CUDA↔CPU")
    ax.plot(s50, c50, "s-", color="#d1495b", lw=2, label="50M  CUDA↔MPS")
    ax.set_xlabel("training step"); ax.set_ylabel("prediction disagreement (%)")
    ax.set_title("Cross-backend divergence emerges with scale")
    ax.legend(frameon=False); ax.grid(alpha=0.25)

    # bar: final-step disagreement by size, 3-seed error bars
    def seed_vals(be, A, B):
        vs = []
        for s in sorted(set(be[A]) & set(be[B])):
            d = pair_disagreement(be[A][s], be[B][s])
            if d is not None:
                vs.append(d)
        return vs
    v10 = seed_vals(be10, "honmaru-cuda", "honmaru-cpu")
    v50 = seed_vals(be50, "honmaru-cuda", "mac-mps")
    means = [statistics.mean(v10), statistics.mean(v50)]
    errs = [statistics.pstdev(v10) if len(v10) > 1 else 0,
            statistics.pstdev(v50) if len(v50) > 1 else 0]
    axb.bar([0, 1], means, yerr=errs, capsize=5,
            color=["#3a7ca5", "#d1495b"], width=0.6)
    axb.axhline(10, ls="--", color="gray", lw=1)
    axb.text(1.45, 10.4, "H1 bar 10%", color="gray", fontsize=8, ha="right")
    axb.set_xticks([0, 1]); axb.set_xticklabels(["10M", "50M"])
    axb.set_ylabel("final disagreement (%)")
    axb.set_title("final step, 3-seed")
    for i, m in enumerate(means):
        axb.text(i, m + errs[i] + 0.4, f"{m:.1f}%", ha="center", fontsize=9)
    fig.tight_layout()
    p = os.path.join(OUT, "fig_h1_scale_emergence.png")
    fig.savefig(p, dpi=600); plt.close(fig)
    return p, means, errs


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
    p1, means, errs = fig_h1(runs)
    p2 = fig_h3(runs)
    print(f"[fig] {p1}  (10M {means[0]:.1f}±{errs[0]:.1f}%, 50M {means[1]:.1f}±{errs[1]:.1f}%)")
    print(f"[fig] {p2}")


if __name__ == "__main__":
    main()
