# -*- coding: utf-8 -*-
"""Plot CPU-vs-MPS divergence on REAL data (shakespeare, generalization regime) vs steps.
Reads runs/skc_<S>.json (CPU) and runs/skm_<S>.json (MPS)."""
import json, glob, re
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

def load(p): return json.load(open(p))
def wmax(A, B):
    m = 0.0
    for n in A["weight_stats"]:
        for k in ("mean", "std", "absmax"):
            m = max(m, abs(A["weight_stats"][n][k] - B["weight_stats"][n][k]))
    return m

steps = sorted(int(re.search(r"skc_(\d+)\.json", p).group(1)) for p in glob.glob("runs/skc_*.json"))
wd, vd, disagree = [], [], []
for S in steps:
    a, b = load(f"runs/skc_{S}.json"), load(f"runs/skm_{S}.json")
    wd.append(wmax(a, b))
    vd.append(abs(a["val_loss"] - b["val_loss"]))
    ag = sum(int(x == y) for x, y in zip(a["val_pred"], b["val_pred"])) / len(a["val_pred"])
    disagree.append(1 - ag)

fig, ax = plt.subplots(1, 2, figsize=(11, 4.2), dpi=150)
ax[0].loglog(steps, wd, "o-", label="weight max|Δ|")
ax[0].loglog(steps, vd, "s-", label="val-loss |Δ|")
ax[0].set_xlabel("training steps"); ax[0].set_ylabel("CPU vs MPS  max|Δ|")
ax[0].set_title("Real data (Shakespeare), generalization regime"); ax[0].legend(fontsize=8)
ax[0].grid(True, which="both", alpha=0.3)

ax[1].semilogx(steps, [d*100 for d in disagree], "^-", color="crimson")
ax[1].set_xlabel("training steps"); ax[1].set_ylabel("val prediction disagreement (%)")
ax[1].set_title("Same seed/data/code, CPU vs MPS → behaviourally different models")
ax[1].grid(True, alpha=0.3)

fig.suptitle("TinyGPT 814k params, fp32, strict — CPU vs Apple MPS on Shakespeare", fontsize=10)
fig.tight_layout()
fig.savefig("analysis/divergence_shakespeare.png", bbox_inches="tight")
print("saved analysis/divergence_shakespeare.png")
print("steps    :", steps)
print("weight Δ :", [f"{x:.1e}" for x in wd])
print("disagree%:", [f"{d*100:.1f}" for d in disagree])
