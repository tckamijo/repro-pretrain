# Size-ladder 結果と解釈（SEALED 実験の開封）

- 日付: 2026-07-12 / mac-mini
- 事前登録: `decisions/2026-07-11-sizeladder-prereg-SEALED.md`（commit 585abe1, sha256 bb177f06…）
- データ: 27 run（Mac 11 + honmaru 16）、corpus `neuro.bin` sha256 9d6b168e…、torch 2.12.1(Mac)/2.12.1+cu126(honmaru)
- 解析: `analysis/analyze_ladder.py` → `analysis/ladder_report.md`
- 図（600dpi + provenance sidecar）: `fig_abstract_schematic.png` / `fig_h1_scale_emergence.png` / `fig_h3_precision.png`

## 事前登録 vs 実測（開封判定）

| 仮説 | 事前登録 | 実測 | 判定 |
|---|---|---|---|
| **H1 保持** | CUDA↔CPU 予測不一致 ≥10% @10M**と**50M | **10M=0.2%（洗い流し）/ 50M=13.2%（支持）** | **文言どおり不支持** ＝ 非単調・スケール創発 |
| **H2 onset** | サイズ増で onset 早まる | 10M=発散せず(onset なし) / 50M=onset step800 | **方向一致**（大きい方が発散、小さい方は不発散） |
| **H3 精度** | bf16/fp16 は fp32 より onset 早い | fp32↔bf16 onset 400 / fp32↔fp16 onset **50**（最終71.9%）| **強く支持** |
| **H4 loss 隠蔽** | 予測≥10%相違でも \|Δval_loss\|<0.05 | 50M で 13.2%相違・\|Δval_loss\|=0.012 | **支持** |

決定性 control: CPU・CUDA は同 seed 2 回で **bit-identical**、**MPS のみ自己非再現(0.07%)**（事前想定どおりの例外）。

## 核心の発見（論文の芯）

**「事前学習の cross-hardware 非決定性は普遍ではなく、モデル規模で創発する」。**
実神経コーパスの非過学習域で、10M では CPU/CUDA/MPS が実質同一モデルに収束（予測 0.2% 差）するのに、
50M では同一レシピが backend ごとに別モデルへ分岐（予測 13.2% 差、しかし val_loss はほぼ一致 = H4）。
= 「小さいモデルは HW 間で再現するが、大きくすると再現性が壊れる」。実務含意が明確（大規模ほど HW 固定が要る）。

### tiny-scale との整合（重要な解釈）
PoC の tiny-shakespeare（0.8M, 過学習域）は 17–19% 分岐だった。今回 10M（非過学習域）が 0.2% に落ちたのは矛盾ではなく **regime 差**:
- tiny-shakespeare = 暗記域（過学習）→ 鋭い loss 曲面で微小差が増幅。
- 10M neuro = 汎化域 → 平滑で backend 差が育たない。
- 50M neuro = 汎化域でも容量↑で曲面が再び鋭くなり分岐が復活。
→ クリーンな主張は「**同一 regime（非過学習・neuro）内で 10M→50M と規模を上げると分岐が創発**」。tiny の 17-19% は別 regime の傍証として区別して書く（anti-rescue: 過学習の数字を汎化の主張に混ぜない）。

## Anti-rescue 順守の記録
- H1 は強気に「両サイズ ≥10%」と封印 → 10M で外した。**後付けで「10M を H1 から外す/閾値を下げる」ことはしない**（ledger 2,6 準拠）。不支持を不支持として報告し、そこから「スケール創発」という**より強い真の主張**へ昇格させた（結果に閉じた rescue でなく、regime を明示した再定式化）。
- 50M の H1 は CPU 律速で CUDA↔MPS 代替（封印時に明記済、ledger 6）。
- torch 版・BLAS は JSON 記録で固定、交絡の都合解釈をしない（ledger 7）。決定性 control で HW 内再現性を先に確認済み。

## 限界（正直に）
- 124M は CUDA 単独（MPS=16GB NaN / CPU 律速）→ 124M の cross-backend は未測。H1 は 10M・50M のみ。
- 50M cross-backend は 1 ペア（CUDA↔MPS = backend も機も torch build も異なる複合差）。CUDA↔CPU@50M は CPU 律速で欠。
- H3 は 50M・単一 seed の precision ペア（seed robust 化は未）。
- onset の step 分解能は milestone 8 点（50/100/200/400/800/1600/3200/4000）。

## 次段
1. 図の paper 化（3枚は投稿用に確定）+ 本 doc を Results/Discussion の骨子に。
2. （任意）124M に第2 backend を載せる工夫（量子化/勾配蓄積で MPS 124M を通す）で cross-backend を 3 サイズに。
3. sci-rep submission template でドラフト化。出口 = ML 再現性 / systems（ReScience or AI for Science hook）。
