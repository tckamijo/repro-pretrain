# Ladder 拡張 結果（SEALED 開封）

- 日付: 2026-07-20 / mac-mini
- 事前登録: `decisions/2026-07-19-ladder-extension-prereg-SEALED.md`（commit 3bff416, sha256 1002eda…）
- 契機: 査読者 Pedro Reviriego（fu2026）「2点でなく 30M/70-80M も測れ」（= 内部 referee M1 と同旨）
- 追加 run: 30M(31.9M) / 75M(72.0M) × {honmaru CUDA, Mac MPS} × 3seed × fp32 × 4000step = 12 run（完走 2026-07-19 15:39）

## 4点 CUDA↔MPS scale 曲線（3-seed 平均 ± SD）

| サイズ | 実 params | 予測不一致 | 判定 | seeds |
|---|---|---|---|---|
| 10M | 10.9M | **0.1% ± 0.1** | washed-out | 0.1/0.0/0.1 |
| **30M** | 31.9M | **11.1% ± 2.3** | material | 13.1/12.3/8.0 |
| 50M | 49.7M | **13.2% ± 1.0** | material | 11.9/14.3/13.4 |
| **75M** | 72.0M | **13.9% ± 0.4** | material | 13.5/13.9/14.4 |

## 事前登録判定（HE1/HE2）

- **HE1（単調増加）→ ✅ 支持**: 0.1 ≤ 11.1 ≤ 13.2 ≤ 13.9（弱単調）、**75M ≥ 50M** ✓、30M ∈ [0.1, 13.2] ✓。
- **HE2（30M が遷移域 5–13%）→ ✅ 支持**（11.1% ∈ [5,13]）。

## 発見の"形"（2点では見えなかった構造）
単なる単調増加でなく **急発現 + 飽和**:
- **10M→30M で急上昇**（0.1% → 11.1%）＝遷移は **10M〜30M 区間に局在**。
- **30M→50M→75M はほぼ横ばい**（11.1 → 13.2 → 13.9）＝~11–14% で **飽和（sub-linear）**。
- 正直な注: **30M は seed 分散大**（±2.3、1 seed が 8.0%）＝遷移端で揺れる。50M/75M は tight（±1.0/±0.4）。
- step 曲線（seed0）: 11M は最後まで平坦、32/50/72M は step 400–800 で発現し以降 ~11–14%。

## 位置づけ更新（本文へ反映）
- **「2点 first probe」→「4点 curve」に格上げ**。scale 依存は「単調に増える」だけでなく
  **「小規模で washed-out → 10M〜30M で急発現 → 以降飽和」**と characterize。
- HE1 を**事前登録して支持**（post-hoc でなく予測を当てた）＝信頼性さらに向上。
- 依然として cross-system（backend+machine+build）交絡は残る（新点も CUDA↔MPS）→ attribution は「numerical path 単独」でなく cross-system のまま。飽和の機構（容量/損失曲面）は未解明＝future work。
- 図 `fig_h1_scale_emergence.png` を4点カーブ版に更新済。
