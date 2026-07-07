# -*- coding: utf-8 -*-
"""Plot cross-backend / MPS run-to-run divergence vs training steps (does it grow?).

Reads runs/sw_{cpu,mps_a,mps_b}_<S>.json produced by the steps sweep.
"""
import json, glob, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def load(p): return json.load(open(p))
def loss_maxabs(a, b): return max(abs(x-y) for x, y in zip(a, b))
def weight_maxabs(A, B):
    m = 0.0
    for name in A["weight_stats"]:
        sa, sb = A["weight_stats"][name], B["weight_stats"].get(name, {})
        for k in ("mean","std","absmax"):
            if k in sb: m = max(m, abs(sa[k]-sb[k]))
    return m

steps = sorted({int(re.search(r"sw_cpu_(\d+)\.json", p).group(1))
                for p in glob.glob("runs/sw_cpu_*.json")})
cm_w, cm_l, mm_w, finals = [], [], [], []
for S in steps:
    cpu = load(f"runs/sw_cpu_{S}.json")
    mpsa = load(f"runs/sw_mps_a_{S}.json")
    mpsb = load(f"runs/sw_mps_b_{S}.json")
    cm_w.append(weight_maxabs(cpu, mpsa))
    cm_l.append(loss_maxabs(cpu["loss"], mpsa["loss"]))
    mm_w.append(weight_maxabs(mpsa, mpsb))
    finals.append((cpu["loss"][-1], mpsa["loss"][-1]))

fig, ax = plt.subplots(1, 2, figsize=(11, 4.2), dpi=150)
ax[0].loglog(steps, cm_w, "o-", label="CPU vs MPS  (weight max|Δ|)")
ax[0].loglog(steps, cm_l, "s-", label="CPU vs MPS  (loss max|Δ|)")
ax[0].loglog(steps, mm_w, "^--", label="MPS run-to-run (weight max|Δ|)")
ax[0].set_xlabel("training steps"); ax[0].set_ylabel("max |Δ|")
ax[0].set_title("Numerical divergence amplifies over training")
ax[0].legend(fontsize=8); ax[0].grid(True, which="both", alpha=0.3)

ax[1].semilogx(steps, [f[0] for f in finals], "o-", label="CPU final loss")
ax[1].semilogx(steps, [f[1] for f in finals], "x--", label="MPS final loss")
ax[1].set_xlabel("training steps"); ax[1].set_ylabel("final loss")
ax[1].set_title("Same seed, same corpus → models split apart")
ax[1].legend(fontsize=8); ax[1].grid(True, alpha=0.3)

fig.suptitle("TinyGPT (110k params, fp32, strict determinism) — CPU vs Apple MPS", fontsize=10)
fig.tight_layout()
out = "analysis/divergence_growth.png"
fig.savefig(out, bbox_inches="tight")
print("saved", out)
print("steps      :", steps)
print("CPUvsMPS wΔ:", [f"{x:.1e}" for x in cm_w])
print("finals     :", [f"{a:.4f}/{b:.4f}" for a,b in finals])
