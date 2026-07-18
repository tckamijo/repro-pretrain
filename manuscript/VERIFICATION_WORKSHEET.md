# 著者検証ワークシート — repro-pretrain（投稿前に著者本人がチェック）

目的: arXiv/TMLR の「著者が生成内容を**自ら検証**した」を実体化する。各主張を出典と突き合わせ、
自分で確認して `[x]` を付ける。**未確認の項目が残る間は投稿しない。** 疑義があれば本文を修正 or 主張を弱める。

正典出典:
- 数値: `analysis/ladder_report.md`（行番号明記）/ 生データ `runs/ladder_*.json`（再計算は `analysis/analyze_ladder.py`）
- 封印: `decisions/2026-07-11-sizeladder-prereg-SEALED.md`（commit 585abe1）/ コーパス: `decisions/2026-07-10-step2-neuro-corpus.md`
- アーキ/手続: `harness/train_scale.py`

## A. 定量主張 → 出典（各行を自分で突き合わせる）

| # | 本文の主張 | 値 | 出典 | 確認 |
|---|---|---|---|---|
| A1 | 総 run 数 | 27（Mac 11 + honmaru 16）| `ladder_report.md:39` + coverage 一覧 / `ls runs/ladder_*.json` | [x] |
| A2 | CPU・CUDA は同seed2回で bit-identical | 0.00%, bit_identical=True | `ladder_report.md:32-34` | [x] |
| A3 | MPS は自己非再現 | 0.07%, bit_identical=False | `ladder_report.md:35` | [x] |
| A4 | 10M CUDA↔CPU 予測不一致 | 0.2%（3 seed）| `ladder_report.md:10` | [x] |
| A5 | 10M 全 backend ペア | 0.1–0.2% | `ladder_report.md:10-15` | [x] |
| A6 | 50M CUDA↔MPS 予測不一致 | 13.2% ± 1.0%（3 seed, SD）| `ladder_report.md:18`（平均）/ SD は `analysis/plot_ladder.py` の pstdev 出力 | [x ] |
| A7 | H4: 50M で \|Δval_loss\| | 0.0121（<0.05）| `ladder_report.md:18`（H4 dval_loss max）| [x] |
| A8 | H2: 10M は onset なし（最終 0.3%）| onset None, 最終 0.3% | `ladder_report.md:22` | [x] |
| A9 | H2: 50M onset step 800（9.2%）、≥10%到達は 1600 | 曲線 9.2/12.3/10.8/11.9 | `ladder_report.md:23` | [x] |
| A10 | H3: fp32↔bf16 onset 400、最終 13.6% | 曲線 …14.8/19.5/15.4/12.9/13.6 | `ladder_report.md:27` | [x] |
| A11 | H3: fp32↔fp16 onset ≤50（6.4%@50）、最終 71.9%（非単調）| 曲線 6.4/…/51.8/45.1/25.7/71.9 | `ladder_report.md:28` | [x] |
| A12 | torch 版 | Mac 2.12.1 / honmaru 2.12.1+cu126 | `ladder_report.md:39` + 各 run JSON `torch` フィールド | [x] |
| A13 | コーパス | 300.12MB, 6961 docs（CC-BY 6933+CC0 28, NC/ND 0）| `decisions/2026-07-10-step2-neuro-corpus.md`「本 crawl 結果」 | [x] |
| A14 | neuro.bin sha256 | 9d6b168e…5b0a27 | 同上 / `runs/FINALIZE_DONE.txt` | [x] |
| A15 | モデル寸法（10M/50M/124M）| d384L6H6/d640L10H10/d768L16H12 | `harness/train_scale.py` SIZES + Methods 表 | [x] |
| A16 | 4000 steps・milestone 8点 | [50,100,200,400,800,1600,3200,4000] | `harness/train_scale.py` milestones | [x] |
| A17 | 封印 commit / sha256 | 585abe1 / bb177f06… | `git log`（SEAL commit）+ `shasum -a256` sealed doc | [x] |

**再現チェック（推奨）**: `.venv/bin/python analysis/analyze_ladder.py` を自分で回し、A2–A11 が上表と一致するのを目視。

## B. 引用の検証（実在するか＋"うちが帰属させた主張"を本当に言っているか）

| key | うちが帰属させた内容 | 出典 | 実在? | 主張一致? |
|---|---|---|---|---|
| srivastava2024verifiable | GPUアーキ間で同accuracy・別予測（H4 の先行） | arXiv:2403.09603 | [x] | [x] |
| fu2026beyond | **inference** 非決定性は 270M–12B で size 無関係 | arXiv:2601.06118 | [x] | [x] |
| shanmugavelu2024fpna | FP非結合の HPC/DL 再現性影響 | arXiv:2408.05148 | [x] | [x] |
| yuan2025llminfer | LLM inference の数値的非決定性 | arXiv:2506.09501 | [x] | [x] |
| li2025crossbackend | deployment cross-backend drift 検出 framework | arXiv:2509.06977 | [x] | [x] |
| chen2022trainrepro | training 再現性 taxonomy | ICSE 2022 / arXiv:2202.02326 | [x] | [x] |
| goldberg1991 | FP非結合は textbook | ACM Comput Surv 1991 | [x] | [x] |
| summers2021 / zhuang2022 | 訓練の不安定/非決定性 | ICML2021 / MLSys2022 | [x] | [x] |
| bouthillier2021 / henderson2018 / pineau2021 | 分散を1級量として扱う方法論 | MLSys2021 / AAAI2018 / JMLR2021 | [x] | [x] |
| kaplan2020 | scaling laws | arXiv:2001.08361 | [x] | [x] |

- **要確認の残**: `bouthillier2021` / `pineau2021` の full author（現 "and others"）を確定（`refs.bib`）。

## C. 事実・手続き主張（自分の理解と一致するか）

- [x] コーパスは PMC OA subset・CC0/CC-BY/CC-BY-SA のみ gate（NC/ND 除外）＝ライセンス的に release 可
- [x] 決定性 control は "achieved"（要求だけでなく実測 bit 一致、CUDA mem-eff attention 警告下でも）
- [x] 124M は CUDA 単独（MPS=16GB NaN / CPU 律速）＝ H1 は 10M/50M のみ、の feasibility 記述が正確
- [x] 50M の H1 は CUDA↔CPU 不可のため **CUDA↔MPS 代替**（backend+machine+build の複合交絡）と正直に明記
- [x] 主張の強さ: 「scale 創発」は **post-hoc・2点・first probe**、inference との対比は open question（overclaim してない）
- [x] 事前登録の仮説・閾値は封印後**未変更**、H1 は refute として報告

## D. 著者オーナーシップ確認（全部済んだら）

- [x] A/B/C を全て自分で確認した
- [x] 各 figure（Fig1–3）を見て、キャプションの数値・軸・誤差棒定義が正しいと確認した
- [x] 全体を通読し、**すべての主張を査読者に自分の言葉で説明・防御できる**
- [x] AI 利用開示文（`AI_USE_DISCLOSURE.md`）を確認し、範囲が正確だと同意した
- [x] → **この全部にチェックが付いてから投稿する**
