# -*- coding: utf-8 -*-
"""Run a device x steps sweep by subprocess-calling train.py.
Reliable driver (PowerShell foreach over piped-stdin ssh silently no-ops; use this).
Writes runs/<prefix>_<dev>_sk_<S>.json. Usage: python run_sweep.py [prefix]"""
import subprocess, sys, os
PY = sys.executable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAIN = os.path.join(ROOT, "harness", "train.py")
PREFIX = sys.argv[1] if len(sys.argv) > 1 else "hm"
STEPS = [100, 400, 1600, 3200]
DEVICES = ["cuda", "cpu"]      # edit per machine (mps on Mac)
for S in STEPS:
    for dev in DEVICES:
        out = os.path.join(ROOT, "runs", f"{PREFIX}_{dev}_sk_{S}.json")
        r = subprocess.run([PY, TRAIN, "--device", dev, "--seed", "0", "--strict",
                            "--data", "shakespeare", "--dim", "128", "--layers", "4",
                            "--heads", "4", "--steps", str(S), "--out", out], check=False)
        print("done", dev, S, "rc", r.returncode, "exists", os.path.exists(out), flush=True)
print("ALL-DONE", flush=True)
