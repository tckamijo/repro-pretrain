# Size-ladder analysis (SEALED 2026-07-11)

glob: `/Users/tadanobukamijo/projects/repro-pretrain/runs/ladder_*.json` | runs: 27

Sealed pre-reg: decisions/2026-07-11-sizeladder-prereg-SEALED.md (585abe1). Thresholds fixed there; this only computes.

## H1 persistence + H4 loss-hiding

### size 10m — backends present: ['honmaru-cpu', 'honmaru-cuda', 'mac-cpu', 'mac-mps']
- honmaru-cpu <-> honmaru-cuda: disagree **0.2%** (seeds [0, 1, 2]) [WASHED-OUT (<5%)] | H4 |dval_loss|max=0.0001 loss_hides=True  <-- sealed H1 pair (CUDA<->CPU)
- honmaru-cpu <-> mac-cpu: disagree **0.1%** (seeds [0, 1, 2]) [WASHED-OUT (<5%)] | H4 |dval_loss|max=0.0001 loss_hides=True
- honmaru-cpu <-> mac-mps: disagree **0.1%** (seeds [0, 1, 2]) [WASHED-OUT (<5%)] | H4 |dval_loss|max=0.0002 loss_hides=True
- honmaru-cuda <-> mac-cpu: disagree **0.1%** (seeds [0, 1, 2]) [WASHED-OUT (<5%)] | H4 |dval_loss|max=0.0000 loss_hides=True  <-- sealed H1 pair (CUDA<->CPU)
- honmaru-cuda <-> mac-mps: disagree **0.1%** (seeds [0, 1, 2]) [WASHED-OUT (<5%)] | H4 |dval_loss|max=0.0000 loss_hides=True
- mac-cpu <-> mac-mps: disagree **0.1%** (seeds [0, 1, 2]) [WASHED-OUT (<5%)] | H4 |dval_loss|max=0.0000 loss_hides=True

### size 50m — backends present: ['honmaru-cuda', 'mac-mps']
- honmaru-cuda <-> mac-mps: disagree **13.2%** (seeds [0, 1, 2]) [SUPPORT (>=10%)] | H4 |dval_loss|max=0.0121 loss_hides=True  <-- 50m H1 substitute (CUDA<->MPS; no CPU at 50m)

## H2 onset (disagreement vs step; onset = first step > 1.0%)

- 10m honmaru-cuda<->honmaru-cpu s0: onset≈**None** | 50:0.0% 100:0.0% 200:0.0% 400:0.0% 800:0.0% 1600:0.0% 3200:0.0% 4000:0.3%
- 50m honmaru-cuda<->mac-mps s0: onset≈**800** | 50:0.0% 100:0.0% 200:0.0% 400:0.2% 800:9.2% 1600:12.3% 3200:10.8% 4000:11.9%

## H3 precision (50m CUDA fp32 vs bf16/fp16, same seed)

- fp32<->bf16 s0: onset≈**400** | 50:0.3% 100:0.2% 200:0.4% 400:14.8% 800:19.5% 1600:15.4% 3200:12.9% 4000:13.6%
- fp32<->fp16 s0: onset≈**50** | 50:6.4% 100:11.4% 200:14.4% 400:51.8% 800:45.1% 1600:25.7% 3200:24.7% 4000:71.9%

## Determinism control (_rep vs base, same seed)

- 10m honmaru-cuda fp32 s0: bit_identical=True pred_disagree=0.00% @step4000
- 50m honmaru-cuda fp32 s0: bit_identical=True pred_disagree=0.00% @step4000
- 10m mac-cpu fp32 s0: bit_identical=True pred_disagree=0.00% @step4000
- 10m mac-mps fp32 s0: bit_identical=False pred_disagree=0.07% @step4000

## Coverage / provenance

- runs loaded: 27 | torch versions: ['2.12.1', '2.12.1+cu126']
  - 10m honmaru-cpu fp32 s0: final_step=4000 nsnaps=8 torch=2.12.1+cu126
  - 10m honmaru-cpu fp32 s1: final_step=4000 nsnaps=8 torch=2.12.1+cu126
  - 10m honmaru-cpu fp32 s2: final_step=4000 nsnaps=8 torch=2.12.1+cu126
  - 10m honmaru-cuda fp32 s0: final_step=4000 nsnaps=8 torch=2.12.1+cu126
  - 10m honmaru-cuda fp32 s0_rep: final_step=4000 nsnaps=8 torch=2.12.1+cu126
  - 10m honmaru-cuda fp32 s1: final_step=4000 nsnaps=8 torch=2.12.1+cu126
  - 10m honmaru-cuda fp32 s2: final_step=4000 nsnaps=8 torch=2.12.1+cu126
  - 10m mac-cpu fp32 s0: final_step=4000 nsnaps=8 torch=2.12.1
  - 10m mac-cpu fp32 s0_rep: final_step=4000 nsnaps=8 torch=2.12.1
  - 10m mac-cpu fp32 s1: final_step=4000 nsnaps=8 torch=2.12.1
  - 10m mac-cpu fp32 s2: final_step=4000 nsnaps=8 torch=2.12.1
  - 10m mac-mps fp32 s0: final_step=4000 nsnaps=8 torch=2.12.1
  - 10m mac-mps fp32 s0_rep: final_step=4000 nsnaps=8 torch=2.12.1
  - 10m mac-mps fp32 s1: final_step=4000 nsnaps=8 torch=2.12.1
  - 10m mac-mps fp32 s2: final_step=4000 nsnaps=8 torch=2.12.1
  - 124m honmaru-cuda fp32 s0: final_step=4000 nsnaps=8 torch=2.12.1+cu126
  - 124m honmaru-cuda fp32 s1: final_step=4000 nsnaps=8 torch=2.12.1+cu126
  - 124m honmaru-cuda fp32 s2: final_step=4000 nsnaps=8 torch=2.12.1+cu126
  - 50m honmaru-cuda bf16 s0: final_step=4000 nsnaps=8 torch=2.12.1+cu126
  - 50m honmaru-cuda fp16 s0: final_step=4000 nsnaps=8 torch=2.12.1+cu126
  - 50m honmaru-cuda fp32 s0: final_step=4000 nsnaps=8 torch=2.12.1+cu126
  - 50m honmaru-cuda fp32 s0_rep: final_step=4000 nsnaps=8 torch=2.12.1+cu126
  - 50m honmaru-cuda fp32 s1: final_step=4000 nsnaps=8 torch=2.12.1+cu126
  - 50m honmaru-cuda fp32 s2: final_step=4000 nsnaps=8 torch=2.12.1+cu126
  - 50m mac-mps fp32 s0: final_step=4000 nsnaps=8 torch=2.12.1
  - 50m mac-mps fp32 s1: final_step=4000 nsnaps=8 torch=2.12.1
  - 50m mac-mps fp32 s2: final_step=4000 nsnaps=8 torch=2.12.1
