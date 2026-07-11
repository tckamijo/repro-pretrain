# Size-ladder 実験 事前登録（PRE-REGISTRATION）— DRAFT（未 seal）

- 起草: 2026-07-11 / mac-mini
- 状態: **SEALED（2026-07-11）**。先生確認済: H1 閾値 10%+3バンド採用 / H2 方向「早まる」確定。
  封印後は仮説・閾値・KILL 基準を変更しない（変更は anti-rescue 違反）。封印 commit hash 後にのみ 50M/124M 実 run・解析に着手。
- 前提: Step2 コーパス確定（`neuro.bin` sha256 `9d6b168e700a2a7b4bd2bbc609449ff6e74952819a0453c3ac0b82d93a5b0a27`, 300.12MB, CC-BY/CC0 100%）。
- 依拠する既往（tiny-scale, seal 前に確立済）: `project_repro_pretrain_2026-07-07` PoC/caveat-kill/capstone。
  tiny-shakespeare 0.8M params 3200 steps で **CPU↔MPS/CUDA の下流予測不一致 17–19%（3-seed robust 18.3%±0.8%）、val_loss はほぼ一致（~1.86）**。
  低精度は onset を早める（fp32 6.2% < bf16 15.2% @400 steps）。CPU/CUDA は run 間 bit-identical、MPS は自己非再現(~1e-6)。

## 核心問い（seal 対象）
tiny×合成/汎化域で観測した「HW/backend 由来の数値非決定性が学習で超線形増幅し、val_loss は揃うのに予測が別モデルに分岐」現象は、
**実神経コーパス（暗記容量を超える非過学習域）× 実用規模（10M–124M）でも保持されるか。**

## 事前登録仮説（結果を見る前に固定）

- **H1（persistence／最優先）**: 実 neuro.bin・非過学習域で、最終 step の
  **CUDA↔CPU 下流予測不一致率が 10M と 50M の両サイズで ≥ 10%**（＝スケールで洗い流されない）。
  閾値 10% の根拠: tiny-scale は 17–19%。10% は「実規模でも tiny の半分以上残る」を要求する強い(＝反証されやすい)予想。
  - **結果バンド（事前確定、単純○×でなく3段で記録）**:
    - **≥10%** = H1 支持（保持）
    - **5–10%** = 保持だが減衰（H1 は文言どおり不支持、現象は生存＝claim を「減衰しつつ保持」に）
    - **<5%** = 洗い流された（tiny 特有、テーゼ downgrade）
  - 方向サブ主張: 固定 step での不一致率は**モデルサイズ増加で減少しない**（flat〜増加を予測）。
- **H2（onset のスケール方向）**: 数値発散が ~1e-6（重み）→巨視的（予測分岐）へ転じる onset step は、
  **モデルサイズ増加で早まる**（大モデルほど少ない step で分岐が顕在化）と予測。
- **H3（precision）**: bf16/fp16 は fp32 より onset が早い（tiny の H3 を実規模へ拡張）。
- **H4（val_loss の隠蔽）**: 分岐したモデル間で val_loss はほぼ一致（|Δval_loss| < 0.05）のに予測は ≥10% 相違
  ＝集計量が HW 由来分岐を隠す、が実規模でも成立。（不一致の「意味あり」バーは H1 と統一して 10%。）

## 検証可能性の正直な境界（design honesty）
pilot 実測より **cross-backend が成立するサイズは 10M・50M**。
**124M は CUDA 単独**（MPS=16GB 天井で NaN、CPU=律速で 4000 steps 非現実）。
→ H1/H4 の cross-backend 検証は **10M・50M が主**、124M は within-backend の錨（run 間決定性 + seed 分岐のみ）。
この制約は seal 時点で既知・明記（後付けで 124M を H1 から外すのは不可）。

## Run matrix（overnight、feasible 版）
- corpus: `neuro.bin`（上記 sha256）。steps=4000、snapshot 指紋で全 step 曲線。
- seeds: {0,1,2}。probe: 固定 val 系列の次トークン argmax 一致率（train_scale の val_pred）。
- 精度: 主軸 fp32。H3 用に 50M×CUDA×seed0 で {bf16, fp16} 追加。
- backend×machine×size:
  | size | honmaru CUDA | honmaru CPU | Mac MPS | Mac CPU |
  |---|---|---|---|---|
  | 10M | ✓ s0-2 | ✓ s0-2 | ✓ s0-2 | ✓ s0-2 |
  | 50M | ✓ s0-2 | – (律速) | ✓ s0-2 | – (律速) |
  | 124M | ✓ s0-2 | – | – (NaN) | – |
- 実行規律: **honmaru は venv python 絶対パス**（`...\.venv\Scripts\python.exe`、bare python=global torch2.6.0 の罠）。
  各 run JSON に torch 版自動記録（train_scale line144）で自己申告。CUBLAS_WORKSPACE_CONFIG は import 前（対応済）。
- 概算: honmaru CUDA 10M 6分/50M 20分/124M 88分・CPU10M 81分、Mac MPS 50M 65分。honmaru/Mac 並行。

## KILL / 反証基準（事前確定）
- **H1 判定（バンド）**: 10M・50M 両方で **≥10% → 支持** / どちらかが **5–10% → 減衰しつつ保持（文言不支持）** / 両方 **<5% → 洗い流される（tiny 特有・テーゼ downgrade）**。
- **H2 反証**: onset step がサイズ増加で**遅くなる or 不変** → 「早まる」予測は不支持。
- **H3 反証**: bf16/fp16 の onset が fp32 と同等以上に遅い。
- **H4 反証**: 予測が ≥10% 相違する run 対で |Δval_loss| ≥ 0.05（loss も明確に違う＝隠蔽でなく普通の性能差）。
- どれか反証でも「現象は実規模で保持」テーゼは downgrade（claim を tiny-scale 限定に）。

## Anti-rescue ledger（封印後に禁止する後付け）
1. probe（val 系列/一致率定義）を結果を見てから変更しない。
2. 「substantial（10%）」閾値・3バンド境界（5%/10%）を結果に合わせて動かさない。
3. 不都合な seed を outlier として落とさない（3-seed 誤差棒で判断）。
4. 分岐が出るまで steps を延長しない（4000 固定）。
5. 「val_loss 揃うのに予測違う」を、結果次第で H4 支持/不支持どちらにも読み替えない（事前に |Δ|<0.05 で固定）。
6. 124M を「cross-backend 不可」と後から言い訳にして H1 を 10M/50M に事後縮小しない（seal 時点で明記済）。
7. torch 版/BLAS/driver 差を、都合よく「交絡」扱いにも「無関係」扱いにも後付けしない（版は JSON 記録で固定）。

## 封印手続き
1. 先生確認 → 本 doc を `-SEALED.md` に改名。
2. commit（本文の sha256 を commit message に記録）= time-gate 起点。
3. 封印 commit hash 記録**後にのみ** 50M/124M の実 run・解析に着手。
