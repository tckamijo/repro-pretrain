# -*- coding: utf-8 -*-
"""Scale-capable reproducibility harness (byte-level, memmap corpus, size presets).

One long run snapshots weight-fingerprint + val predictions at milestone steps, so a
single (size,backend,seed) run yields the whole step-curve (cheap for expensive runs).

  python train_scale.py --device cuda --seed 0 --strict --size 50m \
      --corpus corpus/data/neuro.bin --steps 4000 --out runs/s50_cuda_s0.json
If --corpus is omitted a deterministic synthetic byte stream is used (for pilot timing).
"""
import os, sys
# CUBLAS determinism must be set BEFORE torch imports (CUDA matmul determinism / mitigation axis)
if "--strict" in sys.argv:
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
import argparse, json, hashlib, random, math
import numpy as np
import torch, torch.nn as nn, torch.nn.functional as F

VOCAB = 256  # byte-level
SIZES = {  # (dim, layers, heads, block) — labelled by approx transformer params
    "s":    (128, 2,  2,  128),
    "10m":  (384, 6,  6,  256),
    "30m":  (512, 10, 8,  256),   # 31.9M — ladder extension (Reviriego review)
    "50m":  (640, 10, 10, 256),
    "75m":  (704, 12, 11, 256),   # 72.0M — ladder extension (Reviriego review)
    "124m": (768, 16, 12, 512),
}

def load_corpus(path, synth_tokens=1_000_000):
    if path and os.path.exists(path):
        arr = np.memmap(path, dtype=np.uint8, mode="r")
    else:
        rs = np.random.RandomState(1234)
        arr = rs.randint(0, VOCAB, size=(synth_tokens,), dtype=np.uint8)
    n = int(len(arr) * 0.995)
    return arr[:n], arr[n:]

def get_batch(data, step, batch, block, device):
    g = torch.Generator().manual_seed(9999 + step)          # fixed data order (not --seed)
    ix = torch.randint(0, len(data) - block - 1, (batch,), generator=g).tolist()
    x = torch.from_numpy(np.stack([np.asarray(data[i:i+block], dtype=np.int64) for i in ix]))
    y = torch.from_numpy(np.stack([np.asarray(data[i+1:i+block+1], dtype=np.int64) for i in ix]))
    return x.to(device), y.to(device)

def fixed_val(val, n_seq, block, device):
    stepsz = (len(val) - block - 1) // n_seq
    idx = [k * stepsz for k in range(n_seq)]
    x = torch.from_numpy(np.stack([np.asarray(val[i:i+block], dtype=np.int64) for i in idx]))
    y = torch.from_numpy(np.stack([np.asarray(val[i+1:i+block+1], dtype=np.int64) for i in idx]))
    return x.to(device), y.to(device)

class Block(nn.Module):
    def __init__(self, dim, heads):
        super().__init__()
        self.ln1 = nn.LayerNorm(dim); self.ln2 = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(dim, heads, batch_first=True)
        self.mlp = nn.Sequential(nn.Linear(dim, 4*dim), nn.GELU(), nn.Linear(4*dim, dim))
    def forward(self, x, mask):
        h = self.ln1(x); a, _ = self.attn(h, h, h, attn_mask=mask, need_weights=False)
        x = x + a; return x + self.mlp(self.ln2(x))

class GPT(nn.Module):
    def __init__(self, dim, heads, layers, block):
        super().__init__()
        self.block = block
        self.tok = nn.Embedding(VOCAB, dim); self.pos = nn.Embedding(block, dim)
        self.blocks = nn.ModuleList([Block(dim, heads) for _ in range(layers)])
        self.lnf = nn.LayerNorm(dim); self.head = nn.Linear(dim, VOCAB)
    def forward(self, idx):
        T = idx.size(1)
        mask = torch.triu(torch.ones(T, T, device=idx.device, dtype=torch.bool), 1)
        x = self.tok(idx) + self.pos(torch.arange(T, device=idx.device))[None]
        for b in self.blocks: x = b(x, mask)
        return self.head(self.lnf(x))

def set_determinism(seed, strict):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)
    if strict:
        torch.use_deterministic_algorithms(True, warn_only=True)
        torch.backends.cudnn.deterministic = True; torch.backends.cudnn.benchmark = False

def fingerprint(model):
    h = hashlib.sha256(); s = {}
    for name, p in sorted(model.state_dict().items()):
        a = p.detach().to("cpu", torch.float32).contiguous().numpy()
        h.update(a.tobytes()); s[name] = {"mean": float(a.mean()), "std": float(a.std())}
    return h.hexdigest(), s

def milestones(maxstep):
    out, s = [], 50
    while s < maxstep:
        out.append(s); s = int(s * 2)
    out.append(maxstep); return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu"); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--dtype", default="fp32"); ap.add_argument("--strict", action="store_true")
    ap.add_argument("--size", default="s"); ap.add_argument("--corpus", default="")
    ap.add_argument("--steps", type=int, default=2000); ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--accum", type=int, default=1); ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    dim, layers, heads, block = SIZES[a.size]

    set_determinism(a.seed, a.strict)
    dev = a.device
    train, val = load_corpus(a.corpus)
    model = GPT(dim, heads, layers, block).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr)
    amp = {"fp32": None, "bf16": torch.bfloat16, "fp16": torch.float16}[a.dtype]
    vx, vy = fixed_val(val, 16, block, dev)
    snap_at = set(milestones(a.steps)); snaps = []
    nparams = sum(p.numel() for p in model.parameters())

    def take_snapshot(step):
        model.eval()
        with torch.no_grad():
            vl = float(F.cross_entropy(model(vx).reshape(-1, VOCAB), vy.reshape(-1)).cpu())
            vp = model(vx).argmax(-1).reshape(-1).detach().cpu().tolist()
        sha, st = fingerprint(model)
        snaps.append({"step": step, "val_loss": vl, "val_pred": vp, "sha": sha, "wstats": st})
        model.train()

    losses = []
    model.train()
    import time; t0 = time.time()
    for step in range(1, a.steps + 1):
        opt.zero_grad(set_to_none=True)
        for _ in range(a.accum):
            x, y = get_batch(train, step, a.batch, block, dev)
            if amp is not None and dev != "cpu":
                with torch.autocast(device_type=dev, dtype=amp):
                    loss = F.cross_entropy(model(x).reshape(-1, VOCAB), y.reshape(-1)) / a.accum
            else:
                loss = F.cross_entropy(model(x).reshape(-1, VOCAB), y.reshape(-1)) / a.accum
            loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        losses.append(float(loss.detach().cpu()) * a.accum)
        if step in snap_at: take_snapshot(step)
    dt = time.time() - t0

    out = {"config": vars(a), "arch": {"dim": dim, "layers": layers, "heads": heads, "block": block},
           "n_params": nparams, "torch": torch.__version__, "sec_total": dt,
           "sec_per_step": dt / a.steps, "loss_tail": losses[-5:], "snaps": snaps}
    json.dump(out, open(a.out, "w"))
    print(f"[{dev} {a.size} s{a.seed} {a.dtype} strict={a.strict}] params={nparams/1e6:.1f}M "
          f"{dt:.1f}s ({dt/a.steps*1000:.0f}ms/step) final_loss={losses[-1]:.4f} -> {a.out}")

if __name__ == "__main__":
    main()
