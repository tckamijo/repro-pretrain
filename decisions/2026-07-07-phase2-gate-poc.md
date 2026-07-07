# Phase 2 gate PoC 結果（2026-07-07）

harness（`harness/train.py`、TinyGPT 110,400 params、fixed synthetic corpus、50 steps、fp32、strict）
＋ 比較器（`analysis/compare.py`）で、Phase 2 の gate を Mac mini（CPU / MPS）だけで検証。$0・数秒。

## gate 問い
「決定性フラグ ON で同 backend・同 seed なら bit 再現するか」「異 backend 発散が測れるか」。

## 結果（pairwise、weights_sha256 + loss/weight max|Δ|）
| 比較 | sha一致 | loss max\|Δ\| | weight max\|Δ\| | 判定 |
|---|---|---|---|---|
| CPU s0 × 2（同seed同backend） | **True** | 0 | 0 | **BIT-IDENTICAL** |
| MPS s0 × 2（同seed同backend） | False | 4.8e-7 | 2.5e-6 | NUMERICALLY-CLOSE |
| CPU s0 vs MPS s0（cross-backend） | False | 4.8e-7 | 7.0e-6 | NUMERICALLY-CLOSE |
| CPU s0 vs s1（seed 効果） | False | 8.2e-2 | 4.3e-1 | DIVERGENT |

## 所見（PoC・非 seal）
- **CPU + strict = 完全 bit 再現**（Δ=0）。
- **MPS は strict + 同 seed でも run 間で ~1e-6 の非決定性**（loss は6桁一致だが重み sha 不一致）。CPU との定性差＝本研究の核。
- 効果の階層: **seed(~1e-1〜1e0) ≫ backend差 ≈ MPS run間(~1e-6) ≫ CPU(0)**。
- 計測器（sha 完全一致検出 + tolerance 距離）は3層（bit-identical / numerically-close / divergent）を弁別できる。

## gate 判定: **PASS**
測れる。よって Phase 1（文献・コーパス）と Phase 2 本体（軸を広げて seal）へ進める。

## 次に広げる軸（本実験に向け）
- **backend**: honmaru RTX3060(CUDA/cuDNN) を第3の backend に（今は CPU/MPS のみ）。
- **精度**: bf16 / fp16 / tf32 を追加（低精度ほど分散増の H3 検証）。
- **スケール依存**: steps・params を上げて ~1e-6 の発散が**成長するか**を測る（tiny では小さいが、本番の主眼）。
- **多数 run**: seed を振って run 間分散の分布を取る（1B×1回でなく小型×多数run）。
- honmaru/kuroko/LabPC/無料Colab・Kaggle を backend 軸に追加（cross-machine も）。

## スケール依存（B、2026-07-07 追掘り）＝主眼の予備結果

steps を 50→1600 で振り、各点で CPU vs MPS（同seed strict fp32）と MPS run間の発散を測定。図=`analysis/divergence_growth.png`。

| steps | 最終loss CPU/MPS | loss max\|Δ\| | CPUvsMPS weight max\|Δ\| | MPS run間 weight max\|Δ\| |
|---|---|---|---|---|
| 50 | 4.1047/4.1047 | 4.8e-7 | 7.7e-6 | 1.2e-6 |
| 100 | 3.8799/3.8799 | 9.5e-7 | 3.0e-6 | 9.1e-6 |
| 200 | 3.5746/3.5746 | 9.5e-7 | 4.4e-5 | 4.3e-6 |
| 400 | 2.3422/2.3422 | 1.9e-6 | 3.5e-4 | 1.6e-4 |
| 800 | 0.5596/0.5596 | 2.5e-5 | 6.5e-4 | 2.6e-4 |
| **1600** | **0.3716/0.3784** | **6.0e-2** | **1.2e-2** | **2.3e-2** |

**所見**: cross-backend / MPS run間の発散は **steps とともに超線形に増幅**（~1e-6 → 1e-2、約4桁）。1600 steps で**同seed・同コーパスでも最終 loss が 0.3716 vs 0.3784 に分岐＝実質別モデル**。数値非決定性は良性でなく、**学習を通じ巨視的差に育つ**（butterfly/chaos 増幅）。低 loss（尖った landscape）で加速。

**caveat（正直）**: TinyGPT が固定合成データを**過学習**する領域。実コーパス・大モデル・非過学習域でも増幅するかは本研究の核心問い（＝掘る価値あり）。

**→ B は "育つ" 兆候を確認。novelty 強化。** 次: (a) 実データ/大モデルで増幅の普遍性、(b) 発散が育つ steps 位置と loss/曲率の関係、(c) CUDA(honmaru) 追加。

## caveat-kill: 実データ・汎化域でも増幅（2026-07-07）★核心確認

合成×過学習という caveat を潰すため、**tiny-shakespeare（public domain, char-level）**で
814k params（dim128/L4）を **汎化域**（val loss が下がり続け train と近い＝暗記でない）で学習し、CPU vs MPS を steps sweep。図=`analysis/divergence_shakespeare.png`。

| steps | valCPU/valMPS | weight max\|Δ\| | 下流 val予測 不一致 |
|---|---|---|---|
| 100 | 2.5100/2.5100 | 3.4e-6 | 0.0% |
| 400 | 2.1972/2.1869 | 1.4e-2 | 7.6% |
| 1600 | 1.8940/1.9293 | 1.4e-1 | 14.5% |
| 3200 | 1.8628/1.8810 | 2.2e-1 | **17.6%** |

**結論**:
- caveat 全滅（合成→実データ / 過学習→汎化域 / 110k→814k、どれでも増幅、実データで速い）。
- **so what 確立**: CPU↔MPS の差だけで 3200 steps でモデルが **val予測の 17.6% で食い違う**＝振る舞いレベルで別モデル。
- **鋭い含意**: 3200 で val_loss はほぼ揃う（~1.86）のに予測 17.6% 相違 ＝「同等に良いが別物」。**集計量（loss）がハードウェア由来の分岐を隠す**。
- 現象は robust。→ 本実験（backend階層/精度/onset/緩和策）へ進む価値が確定。

## 3-backend + cross-machine（2026-07-07、honmaru RTX3060 追加）★capstone

honmaru に **torch 2.12.1+cu126（Mac の 2.12.1 と version 完全一致）**を導入し、CUDA を第3 backend に。
同一 harness・同 seed・同データ・同 torch で、**違いは backend/マシンだけ**。図=`analysis/backend_hierarchy.png`。

### ローカル決定性（同機×同backend×同seed×strict）
- Mac-CPU run間 = bit-identical、**honmaru-CUDA run間 = bit-identical**（synthetic）。→ ローカル再現は達成可能。

### backend/機をまたぐと分岐（shakespeare, 予測不一致率%）
| ペア | 100 | 400 | 1600 | 3200 |
|---|---|---|---|---|
| CUDA vs CPU（honmaru内） | 0 | 9.8 | 15.2 | 17.4 |
| MPS vs CPU（Mac内） | 0 | 7.6 | 14.5 | 17.6 |
| **CPU vs CPU（Mac ARM ↔ honmaru AMD, 別機）** | 0 | 7.8 | 14.5 | **17.4** |
| CUDA vs MPS（別機別backend） | 0 | 7.8 | 15.0 | 19.3 |

### 結論（capstone）
- **どの backend/機ペアも 3200 steps で ~17-19% 予測分岐**。増幅は普遍。
- **最強の一撃**: GPU 非決定ですらなく、**同一決定的コードを別 CPU（Apple ARM ↔ AMD x86）で走らせるだけで 17.4% 別モデル**（FP 非結合性がハード間で異なるため）。
- **物語確定**: 「事前学習モデルは同一機×同一backend 上でしか再現しない。GPU/アクセラレータ/CPU を替えれば同じレシピが別モデルを生む」。
- honmaru env: `C:\Users\chuyo\repro-pretrain\.venv`（py3.13 + torch 2.12.1+cu126）、driver 560.94。Python 駆動 `run_sweep.py`（PowerShell foreach は piped-stdin で空振り→Python subprocess 駆動が堅牢）。

## 再現方法
```
cd ~/projects/repro-pretrain
.venv/bin/python harness/train.py --device cpu --seed 0 --strict --out runs/cpu_s0_a.json
.venv/bin/python harness/train.py --device mps --seed 0 --strict --out runs/mps_s0_a.json
.venv/bin/python analysis/compare.py runs/cpu_s0_a.json runs/mps_s0_a.json
```
env: python3.12 venv + torch 2.12.1（MPS 有効）。
