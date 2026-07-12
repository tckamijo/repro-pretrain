# Submission checklist — repro-pretrain（arXiv → TMLR）

順序: **finalize → Zenodo DOI → arXiv（著者版）→ TMLR（匿名版, OpenReview）**。
成果物: arXiv=`manuscript/latex/main.pdf`（著者表示）/ TMLR=`manuscript/latex/main_anon.pdf`（匿名）。
再ビルド: `cd manuscript/latex && ../../.venv/bin/python build_tmlr.py`（著者版）/ `... build_tmlr.py --anon`（匿名版）。

## 0. Finalize（投稿前の詰め）
- [ ] **corresponding email を機関アドレス（u-ryukyu）に差し替え** ── `build_tmlr.py` の `AUTHOR` を編集 → 両版再ビルド。（現状 gmail 暫定）
- [ ] `main.pdf` を通し校正（誤字・図番号・claim が 2点/first probe を超えて主張してないか）。
- [ ] （任意）`bouthillier2021` / `pineau2021` の full author を確定（現 "and others"）。

## 1. Zenodo DOI（コード/成果物を凍結）
- [ ] Zenodo に GitHub でログイン → `tckamijo/repro-pretrain` を有効化。
- [ ] GitHub で release/tag（例 `v1.0-arxiv`）を切る → Zenodo が自動で DOI 発行。
- [ ] その DOI を manuscript の "Data & Code Availability"（`title_page_and_boilerplate.md`）に記入 → 再ビルド。
- メモ: `neuro.bin` は再配布しない（`corpus/collect_neuro.py` + 記録済み sha256 で再構成可能、と既に明記）。

## 2. arXiv（著者版 `main.pdf` / LaTeX ソース）
- [ ] arXiv アカウント。初投稿なら **cs.LG の endorsement** が要る場合あり。
- [ ] primary category = **cs.LG**、cross-list に **cs.PF**（performance）や **stat.ML** を検討。
- [ ] LaTeX ソース一式をアップ（`main.tex + tmlr.sty + tmlr.bst + fancyhdr.sty + refs.bib + fig_*.png 3枚`）で arXiv にコンパイルさせる。※ローカルは `main_anon.tex` 生成もあるので **`main.tex`（著者版）を使う**。
- [ ] ライセンス = **CC-BY 4.0 推奨**（再現性論文の思想と一致）。
- [ ] Comments 欄に「GitHub: …/repro-pretrain ・ Zenodo DOI: … ・ pre-registration sealed 2026-07-11 (commit 585abe1)」を記載。
- [ ] 公開後、arXiv ID を repo の README に追記。

## 3. TMLR（匿名版 `main_anon.pdf` / OpenReview）
- [ ] OpenReview アカウント。
- [ ] **`main_anon.pdf` を投稿**（double-blind）。著者リーク点検: PDF metadata・謝辞・自己引用の言い回し（"our prior work [author]" 等を避ける）。
- [ ] コードリンク: TMLR は preprint 併存 OK だが double-blind PDF 内は **匿名ミラー**（例 anonymous.4open.science）にするのが安全。本文/脚注のリンクは匿名版に。
- [ ] certification/checklist 記入、arXiv preprint がある旨を申告（許可されている）。
- [ ] Action Editor 領域: systems / reproducibility 系。

## 4. 採択後
- [ ] `[accepted]` オプションで再ビルド（`build_tmlr.py` に `--accepted` トグルを足す）。
- [ ] arXiv v2 = camera-ready、repo は公開済み、Zenodo に最終 release。

## 査読で突かれたら出す追加実験（referee_report_1 由来、任意）
- 124M に第2 backend（量子化/勾配蓄積で MPS 124M）→ cross-backend を3サイズ化。
- 50M で same-machine CUDA↔CPU → 交絡断ち。
- H3 の precision 軸を multi-seed 化。
- いずれも `referee_response_1.md` に future work として明記済み。
