# repro-pretrain（仮称）

異種バックエンド（NVIDIA CUDA / Apple MPS / CPU）× seed × 数値精度 における
**小型LM事前学習の再現性・分散**を系統測定する研究。実演台＝神経/生物医学 OA コーパスの小型LM。

- **背骨** = 再現性（rat-voiding の bit-exact cross-env 方法論を確率的事前学習へ拡張）
- **実演台** = ドメイン（神経/生物医学）小型LM。**性能主張はしない**（再現性＋open corpus が売り）
- **$0 first**: 手持ち fleet（honmaru RTX3060 / Mac MPS / LabPC CPU / kuroko CPU）＋無料枠（Kaggle/Colab）で完結。
  1B級スケールアップは grant credit 採択時のオプション（自腹ゼロ）。
- 計画: `~/.claude/plans/giggly-exploring-penguin.md`

## 構造
```
repro-pretrain/
  decisions/   # 設計・事前登録(sealed)・kill/verdict log（正典）
  harness/     # 最小事前学習 harness（PyTorch, backend抽象, seed/決定性フラグ）
  corpus/      # コーパス収集コード（data 本体は gitignore、OA/permissive のみ）
  analysis/    # bit-exact 比較・分散集計（rat-voiding analysis/17,19 を流用）
  runs/        # run 出力（gitignore）
```

## Phase 進捗
- [x] Phase 0: repo 立ち上げ・軸/仮説の骨子起草
- [ ] Phase 1: 二本立て文献収集（1a 手法サーベイ / 1b ドメインコーパス）
- [ ] Phase 2: harness＋パイロット＋**事前登録 seal**（gate: 決定性ON で bit一致・異backendで発散計測）
- [ ] Phase 3: 本実験（seed×backend×精度 の run matrix）
- [ ] Phase 4: 解析・open release（Apache-2.0 code+corpus+weights）・論文
- [ ] Phase 5(opt): 借りGPUで1B級スケールアップ（grant採択時のみ）

## 再利用資産（別repo・READ-ONLY参照）
- `~/projects/rat-voiding-pipeline/analysis/17_cross_platform_diff.py`（bit-exact比較）/ `19_cross_env_matrix.py`（構造発散監査）
- `~/Research/_meta/decisions/2026-07-03-axis1-cross-env-reproducibility.md`（cross-env方法論の正典）
- 事前登録+anti-rescue: `~/Research/_meta/decisions/2026-07-02-aitool-audit-prereg-SEALED.md` 系
- 文献収集3段: `~/Research/_meta/grant-feed/` / `~/projects/tool-radar/`

## 鉄則
- **事前登録は seal 前にデータを見ない**（post-hoc rationalization 回避、anti-rescue ledger 付き）。
- コーパスは **OA/permissive のみ**、provenance を decisions/ に明記。
- 図は artifact-provenance で来歴付与、600dpi。
- code のみ git、data/weights/outputs は gitignore（local-first）。
