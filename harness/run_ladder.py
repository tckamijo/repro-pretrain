#!/usr/bin/env python3
"""harness/run_ladder.py — size-ladder experiment driver (SEALED 2026-07-11).

Pre-registration: decisions/2026-07-11-sizeladder-prereg-SEALED.md
  (commit 585abe1, sha256 bb177f06...). Do NOT change the matrix/steps here
  without a new pre-registration — this drives the sealed experiment.

Runs the machine's slice of the sealed matrix by subprocess-calling
harness/train_scale.py. Uses sys.executable as the interpreter, so LAUNCH THIS
WITH THE VENV PYTHON on each machine:
  honmaru: C:\\Users\\chuyo\\repro-pretrain\\.venv\\Scripts\\python.exe harness\\run_ladder.py --machine honmaru
  mac    : .venv/bin/python harness/run_ladder.py --machine mac
(bare `python` on honmaru = global torch 2.6.0 → would confound the study.)

Each train_scale run records torch.__version__ into its JSON (self-documenting).
Resumable: existing output JSONs are skipped. Corpus = neuro.bin
(sha256 9d6b168e700a2a7b4bd2bbc609449ff6e74952819a0453c3ac0b82d93a5b0a27).
"""
import argparse
import os
import subprocess
import sys
import time

PY = sys.executable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAIN = os.path.join(ROOT, "harness", "train_scale.py")
CORPUS = os.path.join(ROOT, "corpus", "data", "neuro.bin")
RUNS = os.path.join(ROOT, "runs")
STEPS = 4000
SEEDS = (0, 1, 2)

# Sealed matrix, per machine: (size, device, dtype, seeds)
MATRIX = {
    "honmaru": [
        ("10m",  "cuda", "fp32", SEEDS),
        ("10m",  "cpu",  "fp32", SEEDS),
        ("50m",  "cuda", "fp32", SEEDS),
        ("124m", "cuda", "fp32", SEEDS),
        ("50m",  "cuda", "bf16", (0,)),   # H3 precision axis
        ("50m",  "cuda", "fp16", (0,)),   # H3 precision axis
    ],
    "mac": [
        ("10m", "mps", "fp32", SEEDS),
        ("10m", "cpu", "fp32", SEEDS),
        ("50m", "mps", "fp32", SEEDS),
    ],
}

# Determinism control (SEALED): same (size,dev,dtype,seed) run twice -> compare sha.
# CPU/CUDA expected bit-identical; MPS expected self-non-reproducible (~1e-6, documented).
REPLICATES = {
    "honmaru": [("10m", "cuda", "fp32", 0), ("50m", "cuda", "fp32", 0)],
    "mac":     [("10m", "cpu", "fp32", 0),  ("10m", "mps", "fp32", 0)],
}


def jobs(machine):
    for size, dev, dtype, seeds in MATRIX[machine]:
        for s in seeds:
            yield size, dev, dtype, s, ""
    for size, dev, dtype, s in REPLICATES[machine]:
        yield size, dev, dtype, s, "_rep"


def out_path(machine, size, dev, dtype, seed, rep=""):
    return os.path.join(RUNS, f"ladder_{machine}_{size}_{dev}_{dtype}_s{seed}{rep}.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--machine", required=True, choices=list(MATRIX))
    ap.add_argument("--dry", action="store_true", help="print plan, run nothing")
    a = ap.parse_args()
    os.makedirs(RUNS, exist_ok=True)

    plan = list(jobs(a.machine))
    print(f"[ladder] machine={a.machine} interpreter={PY}")
    print(f"[ladder] corpus={CORPUS} exists={os.path.exists(CORPUS)} steps={STEPS} jobs={len(plan)}")
    if a.dry:
        for size, dev, dtype, s, rep in plan:
            done = os.path.exists(out_path(a.machine, size, dev, dtype, s, rep))
            print(f"  {'SKIP' if done else 'RUN '} {size} {dev} {dtype} s{s}{rep}")
        return
    if not os.path.exists(CORPUS):
        sys.exit(f"[ladder] FATAL corpus missing: {CORPUS}")

    done = skipped = failed = 0
    for size, dev, dtype, s, rep in plan:
        outp = out_path(a.machine, size, dev, dtype, s, rep)
        tag = f"{size}/{dev}/{dtype}/s{s}{rep}"
        if os.path.exists(outp):
            print(f"[skip] {tag} (exists)"); skipped += 1; continue
        cmd = [PY, TRAIN, "--device", dev, "--seed", str(s), "--dtype", dtype,
               "--strict", "--size", size, "--corpus", CORPUS,
               "--steps", str(STEPS), "--out", outp]
        t0 = time.time()
        print(f"[run ] {tag} -> {os.path.basename(outp)}", flush=True)
        r = subprocess.run(cmd)
        dt = time.time() - t0
        if r.returncode == 0 and os.path.exists(outp):
            print(f"[done] {tag} ({dt:.0f}s)", flush=True); done += 1
        else:
            print(f"[FAIL] {tag} rc={r.returncode} ({dt:.0f}s)", flush=True); failed += 1
    print(f"[ladder] machine={a.machine} done={done} skipped={skipped} failed={failed}")


if __name__ == "__main__":
    main()
