# Figures — plan and legends

All figures 600 dpi PNG with an `artifact-provenance` sidecar (generating commit, environment,
description). Source: `analysis/plot_ladder.py` (Fig. 2, 3) and `analysis/fig_abstract_schematic.py`
(Fig. 1); data = `runs/ladder_*.json`.

## Fig. 1 — Graphical abstract (`fig_abstract_schematic.png`)
Schematic (standalone; not called out in body per Sci Rep graphical-abstract convention). One
training recipe (same seed, data, code) on CPU/CUDA/MPS yields a near-identical model at 10M
(0.2% prediction disagreement) but divergent "equally-good-but-different" models at 50M (13.2%,
equal loss).

## Fig. 2 — Cross-system divergence by size (`fig_h1_scale_emergence.png`)
**Legend.** *Left:* held-out next-token prediction disagreement (%) versus training step for
10M CUDA↔CPU (seed 0) and 50M CUDA↔MPS (seed 0); disagreement is the percentage of 4,096
fixed-probe positions with differing argmax predictions. *Right:* final-step (step 4,000)
disagreement by model size; bars are the **mean over seeds {0,1,2}** and error bars are **±1
standard deviation** across those three seeds (10M n=3, 50M n=3); dashed line marks the
pre-registered 10% band. The per-step traces (left) are single-seed (seed 0); the bar summary
(right) is three-seed.

## Fig. 3 — Precision and divergence onset (`fig_h3_precision.png`)
**Legend.** Prediction disagreement (%) versus training step at 50M on the CUDA backend,
**single seed (0)**: fp32↔bf16 and fp32↔fp16 (divergence of reduced-precision runs from the
fp32 reference), with the 50M fp32 CUDA↔MPS cross-system pair shown for reference. Onset
(first step > 1%) is ≤ step 50 for fp16 and step 400 for bf16. Traces are single-seed and,
for fp16, non-monotone; endpoint magnitudes are not seed-robust.
