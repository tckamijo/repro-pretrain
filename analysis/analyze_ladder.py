#!/usr/bin/env python3
"""analysis/analyze_ladder.py — evaluate the SEALED size-ladder hypotheses.

Sealed pre-registration: decisions/2026-07-11-sizeladder-prereg-SEALED.md
  (commit 585abe1, sha256 bb177f06...). This computes the metrics the seal
  defines; it does NOT change any threshold.

Inputs : runs/ladder_<machine>_<size>_<dev>_<dtype>_s<seed>[_rep].json
  each with snaps[] = [{step, val_loss, val_pred(list len 4096), sha, wstats}, ...]
  milestones typically [50,100,200,400,800,1600,3200,4000].

Metrics (per seal):
  H1 persistence  : cross-backend final-step prediction disagreement % at 10m/50m.
                    3-band verdict >=10% support / 5-10% diminished / <5% washed out.
                    NOTE the seal named the pair "CUDA<->CPU" at BOTH sizes, but the
                    feasibility table excludes CPU at 50m (too slow). So there is no
                    CPU run at 50m -> at 50m we report CUDA<->MPS as the available
                    cross-backend pair. This substitution is design-honest (recorded
                    at analysis-design time, before results), not a post-hoc rescue.
  H2 onset        : disagreement vs step curve per size; onset = first milestone
                    crossing ONSET_PCT. Compare 10m vs 50m (earlier with size?).
  H3 precision    : 50m CUDA fp32 vs bf16 vs fp16 divergence curve (same backend/seed).
  H4 loss-hiding  : for pairs with disagreement >=10%, report |dval_loss| (<0.05 => hidden).
  determinism ctrl: _rep vs base -> sha bit-identical? + disagreement (CPU/CUDA=0, MPS ~>0).

Usage: python analysis/analyze_ladder.py [--glob 'runs/ladder_*.json']
Deterministic; no network. Writes analysis/ladder_report.md and prints a summary.
"""
from __future__ import annotations

import argparse
import glob as globmod
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPORT = os.path.join(HERE, "ladder_report.md")

ONSET_PCT = 1.0          # disagreement % that marks divergence "macroscopic" (H2)
SUPPORT = 10.0           # H1 support band lower bound (sealed)
WASH = 5.0               # H1 wash-out band upper bound (sealed)
LOSS_HIDE = 0.05         # H4 |dval_loss| below this = loss hides the divergence

NAME_RE = re.compile(
    r"ladder_(?P<machine>\w+?)_(?P<size>\w+?)_(?P<dev>\w+?)_(?P<dtype>\w+?)_s(?P<seed>\d+)(?P<rep>_rep)?\.json$")


def load_runs(pattern):
    runs = {}
    for p in sorted(globmod.glob(pattern)):
        m = NAME_RE.search(os.path.basename(p))
        if not m:
            continue
        try:
            d = json.load(open(p))
        except Exception:
            continue
        snaps = {s["step"]: s for s in d.get("snaps", [])}
        if not snaps:
            continue
        g = m.groupdict()
        key = (g["size"], f"{g['machine']}-{g['dev']}", g["dtype"], int(g["seed"]), bool(g["rep"]))
        runs[key] = {"path": p, "snaps": snaps, "torch": d.get("torch"),
                     "n_params": d.get("n_params"), **g}
    return runs


def disagree(pa, pb):
    """% of positions where two argmax prediction lists differ."""
    n = min(len(pa), len(pb))
    if n == 0:
        return None
    d = sum(1 for i in range(n) if pa[i] != pb[i])
    return 100.0 * d / n


def final_step(run):
    return max(run["snaps"])


def backends_at(runs, size, dtype="fp32", rep=False):
    """map backend -> {seed: run} for a given size."""
    out = {}
    for (sz, be, dt, seed, rp), r in runs.items():
        if sz == size and dt == dtype and rp == rep:
            out.setdefault(be, {})[seed] = r
    return out


def pair_disagreement(rA, rB, step=None):
    """disagreement at a step (default: common final step)."""
    if step is None:
        step = min(final_step(rA), final_step(rB))
    if step not in rA["snaps"] or step not in rB["snaps"]:
        return None
    return disagree(rA["snaps"][step]["val_pred"], rB["snaps"][step]["val_pred"])


def band(pct):
    if pct is None:
        return "n/a"
    if pct >= SUPPORT:
        return "SUPPORT (>=10%)"
    if pct >= WASH:
        return "DIMINISHED (5-10%)"
    return "WASHED-OUT (<5%)"


def h1_and_h4(runs, lines):
    lines.append("## H1 persistence + H4 loss-hiding\n")
    for size in ("10m", "50m"):
        be = backends_at(runs, size)
        lines.append(f"### size {size} — backends present: {sorted(be)}")
        bnames = sorted(be)
        # all cross-backend pairs, seed-matched, averaged over seeds
        for i in range(len(bnames)):
            for j in range(i + 1, len(bnames)):
                A, B = bnames[i], bnames[j]
                seeds = sorted(set(be[A]) & set(be[B]))
                vals, dloss = [], []
                for s in seeds:
                    d = pair_disagreement(be[A][s], be[B][s])
                    if d is None:
                        continue
                    vals.append(d)
                    fa, fb = final_step(be[A][s]), final_step(be[B][s])
                    st = min(fa, fb)
                    dloss.append(abs(be[A][s]["snaps"][st]["val_loss"]
                                     - be[B][s]["snaps"][st]["val_loss"]))
                if not vals:
                    continue
                mean = sum(vals) / len(vals)
                hidden = (max(dloss) < LOSS_HIDE) if dloss else None
                tag = ""
                if {A.split("-")[1], B.split("-")[1]} == {"cuda", "cpu"}:
                    tag = "  <-- sealed H1 pair (CUDA<->CPU)"
                elif size == "50m" and {A.split("-")[1], B.split("-")[1]} == {"cuda", "mps"}:
                    tag = "  <-- 50m H1 substitute (CUDA<->MPS; no CPU at 50m)"
                lines.append(
                    f"- {A} <-> {B}: disagree **{mean:.1f}%** (seeds {seeds}) "
                    f"[{band(mean)}] | H4 |dval_loss|max={max(dloss):.4f} "
                    f"loss_hides={hidden}{tag}")
        lines.append("")


def h2_onset(runs, lines):
    lines.append("## H2 onset (disagreement vs step; onset = first step > "
                 f"{ONSET_PCT}%)\n")
    for size in ("10m", "50m"):
        be = backends_at(runs, size)
        if "honmaru-cuda" not in be:
            continue
        # reference cross-backend pair: prefer cuda<->cpu, else cuda<->mps
        other = "honmaru-cpu" if "honmaru-cpu" in be else ("mac-mps" if "mac-mps" in be else None)
        if other is None:
            continue
        seeds = sorted(set(be["honmaru-cuda"]) & set(be[other]))
        if not seeds:
            continue
        s = seeds[0]
        A, B = be["honmaru-cuda"][s], be[other][s]
        steps = sorted(set(A["snaps"]) & set(B["snaps"]))
        curve = [(st, pair_disagreement(A, B, st)) for st in steps]
        onset = next((st for st, d in curve if d is not None and d > ONSET_PCT), None)
        crv = " ".join(f"{st}:{d:.1f}%" for st, d in curve if d is not None)
        lines.append(f"- {size} honmaru-cuda<->{other} s{s}: onset≈**{onset}** | {crv}")
    lines.append("")


def h3_precision(runs, lines):
    lines.append("## H3 precision (50m CUDA fp32 vs bf16/fp16, same seed)\n")
    ref = None
    for (sz, be, dt, seed, rp), r in runs.items():
        if sz == "50m" and be == "honmaru-cuda" and dt == "fp32" and seed == 0 and not rp:
            ref = r
    if ref is None:
        lines.append("- (fp32 50m CUDA s0 reference not present yet)\n"); return
    for dtype in ("bf16", "fp16"):
        r = runs.get(("50m", "honmaru-cuda", dtype, 0, False))
        if not r:
            lines.append(f"- {dtype}: (missing)"); continue
        steps = sorted(set(ref["snaps"]) & set(r["snaps"]))
        curve = [(st, pair_disagreement(ref, r, st)) for st in steps]
        onset = next((st for st, d in curve if d is not None and d > ONSET_PCT), None)
        crv = " ".join(f"{st}:{d:.1f}%" for st, d in curve if d is not None)
        lines.append(f"- fp32<->{dtype} s0: onset≈**{onset}** | {crv}")
    lines.append("")


def determinism(runs, lines):
    lines.append("## Determinism control (_rep vs base, same seed)\n")
    for (sz, be, dt, seed, rp), r in runs.items():
        if not rp:
            continue
        base = runs.get((sz, be, dt, seed, False))
        if not base:
            lines.append(f"- {sz} {be} {dt} s{seed}: base missing"); continue
        st = min(final_step(r), final_step(base))
        sha_r = r["snaps"][st]["sha"]; sha_b = base["snaps"][st]["sha"]
        dis = pair_disagreement(r, base, st)
        lines.append(f"- {sz} {be} {dt} s{seed}: bit_identical={sha_r == sha_b} "
                     f"pred_disagree={dis:.2f}% @step{st}")
    lines.append("")


def coverage(runs, lines):
    lines.append("## Coverage / provenance\n")
    torches = sorted({r.get("torch") for r in runs.values()})
    lines.append(f"- runs loaded: {len(runs)} | torch versions: {torches}")
    for (sz, be, dt, seed, rp) in sorted(runs):
        r = runs[(sz, be, dt, seed, rp)]
        fs = final_step(r)
        lines.append(f"  - {sz} {be} {dt} s{seed}{'_rep' if rp else ''}: "
                     f"final_step={fs} nsnaps={len(r['snaps'])} torch={r.get('torch')}")
    lines.append("")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default=os.path.join(ROOT, "runs", "ladder_*.json"))
    a = ap.parse_args()
    runs = load_runs(a.glob)
    lines = [f"# Size-ladder analysis (SEALED 2026-07-11)\n",
             f"glob: `{a.glob}` | runs: {len(runs)}\n",
             "Sealed pre-reg: decisions/2026-07-11-sizeladder-prereg-SEALED.md "
             "(585abe1). Thresholds fixed there; this only computes.\n"]
    if not runs:
        lines.append("_No ladder runs found yet._\n")
    else:
        h1_and_h4(runs, lines)
        h2_onset(runs, lines)
        h3_precision(runs, lines)
        determinism(runs, lines)
        coverage(runs, lines)
    open(REPORT, "w").write("\n".join(lines))
    print("\n".join(lines))
    print(f"\n[written] {REPORT}")


if __name__ == "__main__":
    main()
