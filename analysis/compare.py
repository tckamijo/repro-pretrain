# -*- coding: utf-8 -*-
"""Compare two run.json fingerprints from harness/train.py.

Reports: weights_sha256 exact match, loss-trajectory max|Δ| and final |Δ|,
and max|Δ| across weight stats (mean/std/absmax). Cross-backend / cross-run diff.

Usage: python compare.py runs/cpu_s0_a.json runs/cpu_s0_b.json
"""
import argparse, json

def load(p): return json.load(open(p))

def maxabs(a, b): return max(abs(x - y) for x, y in zip(a, b)) if a and b else float("nan")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a"); ap.add_argument("b")
    args = ap.parse_args()
    A, B = load(args.a), load(args.b)
    sha_match = A["weights_sha256"] == B["weights_sha256"]
    loss_max = maxabs(A["loss"], B["loss"])
    loss_final = abs(A["loss"][-1] - B["loss"][-1])
    # weight stats max abs diff
    wmax = 0.0
    for name in A["weight_stats"]:
        sa, sb = A["weight_stats"][name], B["weight_stats"].get(name, {})
        for k in ("mean", "std", "absmax"):
            if k in sb: wmax = max(wmax, abs(sa[k] - sb[k]))
    # downstream behaviour: val loss diff + top-1 argmax agreement on the fixed val batch
    vloss_d = abs(A.get("val_loss", float("nan")) - B.get("val_loss", float("nan")))
    pa, pb = A.get("val_pred"), B.get("val_pred")
    agree = (sum(int(x == y) for x, y in zip(pa, pb)) / len(pa)) if pa and pb else float("nan")
    ca, cb = A["config"], B["config"]
    def tag(c): return f"{c['device']}/s{c['seed']}/{c['dtype']}/{c.get('data','?')}/strict={c['strict']}"
    print(f"A = {tag(ca)}   ({args.a})")
    print(f"B = {tag(cb)}   ({args.b})")
    print(f"  weights_sha256 exact match : {sha_match}")
    print(f"  loss  max|Δ| = {loss_max:.3e}   final|Δ| = {loss_final:.3e}")
    print(f"  weight-stats max|Δ| = {wmax:.3e}")
    print(f"  val_loss |Δ| = {vloss_d:.3e}   downstream top-1 agreement = {agree:.4f}")
    verdict = "BIT-IDENTICAL" if sha_match else ("NUMERICALLY-CLOSE" if wmax < 1e-4 else "DIVERGENT")
    print(f"  -> {verdict}")

if __name__ == "__main__":
    main()
