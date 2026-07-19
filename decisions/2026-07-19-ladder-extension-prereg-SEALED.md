# Ladder 拡張 事前登録（PRE-REGISTRATION）— DRAFT（未 seal）

- 起草: 2026-07-19 / mac-mini
- 状態: **SEALED（2026-07-19）**。先生確認済（HE1 単調増加 / HE2 30M 遷移域）。封印後は予測・閾値を変更しない（anti-rescue）。封印 commit hash 後にのみ run・解析着手。
- 契機: 査読者 Pedro Reviriego（fu2026 著者）の指摘「2点でなく 30M/70-80M など中間・大サイズも測れ」。元の封印 ladder（10M/50M/124M, `decisions/2026-07-11-...-SEALED.md`）を**密にする追試**。
- 依拠既知（結果確定済、封印対象外）: CUDA↔MPS 予測不一致は 10M=0.1%（washed-out）/ 50M=13.2%（3-seed）。124M=CUDA単独で cross-backend 不可。

## 追加サイズ（実測パラメータ数, train_scale.py SIZES）
- **30M** = dim512/L10/H8/blk256 = **31.9M**
- **75M** = dim704/L12/H11/blk256 = **72.0M**
（MPS 載る事を smoke 済: 30M 655ms/step, 75M 1425ms/step, OOM なし。124M と違い 16GB 内。）

## 核心問い（seal 対象）
既存2点（10M washed / 50M 13.2%）を、**同一 regime（実 neuro・非過学習・CUDA↔MPS・fp32・4000step）で 4 点**
（10M・30M・50M・75M）に密にした時、**cross-system 分岐 vs モデル規模の関係が単調に増加するか**。

## 事前登録仮説（結果を見る前に固定）
- **HE1（単調性／主）**: CUDA↔MPS 最終 step 予測不一致率は、実パラメータ数に対して **10M ≤ 30M ≤ 50M ≤ 75M** の
  順に（弱)単調増加する（各 3-seed 平均）。厳密単調でなく、**75M ≥ 50M** かつ **30M は 10M(0.1%)と 50M(13.2%)の間**、を要件とする。
- **HE2（発現閾）**: 分岐が washed-out(<5%)から material(≥10%)へ移る規模境界は 10M と 50M の間にあり、
  **30M でその遷移域（5–13%）に入る**と予測（10M=0.1%, 50M=13.2% の中間なので）。
- **結果バンド（HE1 判定、事前確定）**:
  - **4 点が (弱)単調増加 かつ 75M≥50M** → HE1 支持（scale 依存を"曲線"で確認、2点→4点に格上げ）
  - **非単調（例 75M<50M、または 30M が範囲外）** → HE1 不支持、「単調でない/飽和/非線形」を正直報告
  - **全点が washed-out** → 既存 50M 結果と矛盾（要再検）

## Run matrix（追加分のみ）
- サイズ {30M, 75M} × backend {honmaru CUDA, Mac MPS} × seed {0,1,2} × fp32 × 4000 step = **12 run**
- 既存の 10M/50M と合わせ、CUDA↔MPS を 4 点（10M/30M/50M/75M）で比較。
- 出力名 `runs/ladder_<machine>_<size>_<dev>_fp32_s<seed>.json`（既存 analyze_ladder がそのまま集計）。
- 規律: honmaru は venv python 絶対パス、torch 版自動記録、CUBLAS_WORKSPACE_CONFIG import 前（対応済）。

## Anti-rescue ledger（封印後禁止）
1. 4 点のどれかを「外れ」として結果を見てから落とさない。
2. 単調/非単調の判定基準（75M≥50M・30M∈[10M,50M]）を結果に合わせて動かさない。
3. 非単調が出たら「単調」と言い換えず、非単調をそのまま報告（元論文の非単調正直報告と同じ規律）。
4. 追加点は元 pre-reg とは別の**本拡張 pre-reg**下で解釈（元 H1 の refute 判定は不変）。
5. seed を後から足して都合よく平均を動かさない（3-seed 固定、robust 化は更に別途）。

## 封印手続き
1. 先生確認 → `-SEALED.md` 改名 → commit（本文 sha256 を message に記録）= time-gate。
2. 封印 commit hash 後にのみ 30M/75M run・解析に着手。
