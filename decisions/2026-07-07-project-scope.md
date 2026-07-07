# repro-pretrain 立ち上げ・軸/仮説の骨子（2026-07-07、Phase 0）

> **これは DRAFT（未 seal）**。事前登録の seal は Phase 2 末（harness＋pilot でデータを見る前）。
> ここではデータを見ずに「何を測るか」の骨子だけ固める。流儀: [[feedback_pre_registered_test_anti_rescue]]。

## 問い（core）
$300/小型 時代になって初めて多数 run が可能になった今、**小型LMの事前学習は
「どの環境・seed・数値精度で回すか」でどれだけ結果がぶれるか**。特に **cross-backend
（CUDA/MPS/CPU）決定性**は SOTA 規模では「高すぎて測れない」ため未測 = gap。

## 測る軸（Phase 2 で確定・seal）
- **① seed**: init seed / data-order seed を分離。
- **② backend**: honmaru RTX3060(CUDA/cuDNN) / Mac mini(Apple MPS) / LabPC・kuroko(CPU) / 無料 Colab・Kaggle(T4)。
- **③ 数値精度**: fp32 / tf32 / bf16 / fp16。
- **④ 決定性フラグ**: torch.use_deterministic_algorithms / cudnn.deterministic / thread数・BLAS。

## 測る量（候補、Phase 2 で確定）
- 学習曲線（train/val loss の軌跡）、最終 loss / perplexity。
- grad-norm 系列、重み/埋め込みの cross-run 距離（cos / L2）。
- 下流の簡易 task（ドメイン語彙の穴埋め等）の一致度。
- 構造発散（NaN/shape/欠損）の有無（audit-utility で自動検出）。

## 仮説の骨子（DRAFT・seal で確定）
- H1（決定性）: 決定性フラグ ON かつ **同一 backend・同一 seed** なら bit-reproducible（tolerance 内）。
- H2（cross-backend）: **backend 差**（CUDA vs MPS vs CPU）は seed 差より大きい発散を生む。
- H3（精度）: 低精度（fp16/bf16）ほど run 間分散が増える。
- （閾値・tolerance・run数 は pilot 実測後に seal。1B×1回でなく **小型×多数run** で統計を締める。）

## 再利用（別repo READ-ONLY）
- bit-exact 比較: rat-voiding `analysis/17_cross_platform_diff.py`（tolerance/行正準化/列別）。
- 構造発散監査: `analysis/19_cross_env_matrix.py`（SHAPE_MISMATCH/MISSING 自動検出）。
- cross-env 方法論の正典: `~/Research/_meta/decisions/2026-07-03-axis1-cross-env-reproducibility.md`（atol1e-12/rtol1e-9・BLAS単離）。

## anti-rescue（seal 時に候補と反論を先出しする欄・現状 骨子）
- 「convergence が遅い→iteration を増やす」→ pre-reg の iteration は結果、緩める口実にしない。
- 「ドメインコーパスだから target loss を変える」→ corpus 差は既知、外れたら divergence 所見として報告。
- （seal 時に埋める）

## 次アクション
1. Phase 1a: 手法サーベイ収集（grant-feed/tool-radar 3段を流用）。
2. Phase 1b: 神経/生物医学 OA コーパス収集（PMC OA / bioRxiv、OA・ライセンス確認、provenance）。
3. Phase 2: 最小 harness（PyTorch, backend抽象, seed全経路固定, 決定性フラグ）→ 極小規模で計測器検証 → **seal**。
