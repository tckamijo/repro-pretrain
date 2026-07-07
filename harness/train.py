# -*- coding: utf-8 -*-
"""Minimal reproducibility harness: tiny GPT pretraining with determinism controls.

Isolates *init + compute* determinism: data + batch order are fixed (constant seed,
independent of --seed). Emits run.json (loss/grad-norm trajectory, val_loss,
weight sha256 + stats, and val argmax predictions for downstream-agreement compare).

  python train.py --device mps --seed 0 --strict --data shakespeare --dim 128 --layers 4 \
                  --steps 800 --out runs/x.json
"""
import argparse, json, hashlib, random, os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

BLOCK = 32
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "corpus", "data")

def load_data(source):
    """returns (train_ids: LongTensor, val_ids: LongTensor, vocab: int). 90/10 split."""
    if source == "synthetic":
        rs = np.random.RandomState(1234)
        ids = rs.randint(0, 64, size=(8192,)).astype(np.int64); vocab = 64
    elif source == "shakespeare":
        txt = open(os.path.join(DATA_DIR, "shakespeare.txt"), encoding="utf-8").read()
        chars = sorted(set(txt)); stoi = {c: i for i, c in enumerate(chars)}
        ids = np.array([stoi[c] for c in txt], dtype=np.int64); vocab = len(chars)
    else:
        raise ValueError(source)
    n = int(len(ids) * 0.9)
    return torch.tensor(ids[:n]), torch.tensor(ids[n:]), vocab

def get_batch(data, step, batch, block, device):
    g = torch.Generator().manual_seed(9999 + step)   # fixed order (not --seed)
    ix = torch.randint(0, len(data) - block - 1, (batch,), generator=g)
    x = torch.stack([data[i:i+block] for i in ix]).to(device)
    y = torch.stack([data[i+1:i+block+1] for i in ix]).to(device)
    return x, y

def fixed_val_batch(val, n_seq, block, device):
    """deterministic held-out batch (same across all runs) for val loss + downstream preds."""
    step = (len(val) - block - 1) // n_seq
    idx = [k * step for k in range(n_seq)]
    x = torch.stack([val[i:i+block] for i in idx]).to(device)
    y = torch.stack([val[i+1:i+block+1] for i in idx]).to(device)
    return x, y

class Block(nn.Module):
    def __init__(self, dim, heads):
        super().__init__()
        self.ln1 = nn.LayerNorm(dim); self.ln2 = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(dim, heads, batch_first=True)
        self.mlp = nn.Sequential(nn.Linear(dim, 4*dim), nn.GELU(), nn.Linear(4*dim, dim))
    def forward(self, x):
        h = self.ln1(x)
        mask = torch.triu(torch.ones(x.size(1), x.size(1), device=x.device, dtype=torch.bool), 1)
        a, _ = self.attn(h, h, h, attn_mask=mask, need_weights=False)
        x = x + a
        return x + self.mlp(self.ln2(x))

class TinyGPT(nn.Module):
    def __init__(self, vocab, dim, heads, layers, block=BLOCK):
        super().__init__()
        self.tok = nn.Embedding(vocab, dim); self.pos = nn.Embedding(block, dim)
        self.blocks = nn.ModuleList([Block(dim, heads) for _ in range(layers)])
        self.lnf = nn.LayerNorm(dim); self.head = nn.Linear(dim, vocab)
    def forward(self, idx):
        pos = torch.arange(idx.size(1), device=idx.device)
        x = self.tok(idx) + self.pos(pos)[None]
        for b in self.blocks: x = b(x)
        return self.head(self.lnf(x))

def set_determinism(seed, strict):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)
    if strict:
        torch.use_deterministic_algorithms(True, warn_only=True)
        torch.backends.cudnn.deterministic = True; torch.backends.cudnn.benchmark = False

def weight_fingerprint(model):
    h = hashlib.sha256(); stats = {}
    for name, p in sorted(model.state_dict().items()):
        arr = p.detach().to("cpu", torch.float32).contiguous().numpy()
        h.update(arr.tobytes())
        stats[name] = {"mean": float(arr.mean()), "std": float(arr.std()), "absmax": float(np.abs(arr).max())}
    return h.hexdigest(), stats

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu"); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--dtype", default="fp32"); ap.add_argument("--strict", action="store_true")
    ap.add_argument("--data", default="synthetic")   # synthetic | shakespeare
    ap.add_argument("--dim", type=int, default=64); ap.add_argument("--layers", type=int, default=2)
    ap.add_argument("--heads", type=int, default=2)
    ap.add_argument("--steps", type=int, default=50); ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--lr", type=float, default=3e-3); ap.add_argument("--out", required=True)
    a = ap.parse_args()

    set_determinism(a.seed, a.strict)
    dev = a.device
    train, val, vocab = load_data(a.data)
    model = TinyGPT(vocab, a.dim, a.heads, a.layers).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr)
    amp = {"fp32": None, "bf16": torch.bfloat16, "fp16": torch.float16}[a.dtype]
    vx, vy = fixed_val_batch(val, 16, BLOCK, dev)

    losses, gnorms, vlosses = [], [], []
    for step in range(a.steps):
        model.train()
        x, y = get_batch(train, step, a.batch, BLOCK, dev)
        opt.zero_grad(set_to_none=True)
        if amp is not None and dev != "cpu":
            with torch.autocast(device_type=dev, dtype=amp):
                loss = F.cross_entropy(model(x).reshape(-1, vocab), y.reshape(-1))
        else:
            loss = F.cross_entropy(model(x).reshape(-1, vocab), y.reshape(-1))
        loss.backward()
        gn = torch.nn.utils.clip_grad_norm_(model.parameters(), 1e9)
        opt.step()
        losses.append(float(loss.detach().cpu())); gnorms.append(float(gn.detach().cpu()))
        if step % max(1, a.steps // 20) == 0 or step == a.steps - 1:
            model.eval()
            with torch.no_grad():
                vl = F.cross_entropy(model(vx).reshape(-1, vocab), vy.reshape(-1))
            vlosses.append([step, float(vl.detach().cpu())])

    model.eval()
    with torch.no_grad():
        vpred = model(vx).argmax(-1).reshape(-1).detach().cpu().tolist()   # downstream behaviour
        vloss_final = float(F.cross_entropy(model(vx).reshape(-1, vocab), vy.reshape(-1)).cpu())
    sha, stats = weight_fingerprint(model)
    n_params = sum(p.numel() for p in model.parameters())
    out = {"config": vars(a), "vocab": vocab, "n_params": n_params, "torch": torch.__version__,
           "loss": losses, "grad_norm": gnorms, "val_curve": vlosses, "val_loss": vloss_final,
           "val_pred": vpred, "weights_sha256": sha, "weight_stats": stats}
    json.dump(out, open(a.out, "w"))
    print(f"[{dev} s{a.seed} {a.dtype} {a.data} d{a.dim}L{a.layers} strict={a.strict}] "
          f"params={n_params} train={losses[-1]:.4f} val={vloss_final:.4f} sha={sha[:12]} -> {a.out}")

if __name__ == "__main__":
    main()
