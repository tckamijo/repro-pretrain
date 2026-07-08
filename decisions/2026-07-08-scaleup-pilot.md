# スケールアップ pilot（2026-07-08）

`harness/train_scale.py`（byte-level, memmap corpus, size preset, snapshot 指紋, CUDA 決定性 env）を honmaru/Mac で pilot。

## 1-step 時間（fp32, strict, batch16）
| size | params | CUDA(honmaru RTX3060) | MPS(Mac 16GB) | CPU(honmaru) |
|---|---|---|---|---|
| 10m | 10.9M | 96ms | (速) | 1219ms |
| 50m | 49.7M | 304ms | 980ms | 4864ms |
| 124m | 114.2M | **1314ms** ✓ | 27909ms + **NaN** ✗ | ~20s+ ✗ |

## 判明した制約
- **124m は CUDA だけ現実的**（MPS は Mac 16GB で swap+NaN、CPU も律速）。cross-backend はサイズ上昇で狭まる: 10m=CUDA/MPS/CPU、50m=CUDA/MPS、124m=CUDA中心（run間決定性+精度）。
- CUDA は overnight で 124m を 2万+step 回せる。
- **synthetic random bytes は学習不能**（final_loss≈ln256=5.55）→ **実データ（神経OAコーパス）が必須**。overnight の前に Step2 必要。

## 次
Step2 神経OAコーパス収集 → 事前登録 seal → overnight（feasibleな backend×size matrix）。
