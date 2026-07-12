# Venue decision: TMLR (Transactions on Machine Learning Research)

- 日付: 2026-07-12
- 決定: **TMLR** を投稿先に確定。

## なぜ TMLR（Fit-first）
改訂後の論文は「2サイズ・単一交絡・一部単一seed の **rigorous な測定 + 再現 instrument**」で、
claim は控えめ・process は一級。→ **novelty でなく correctness/rigor で評価する場**が最適。

- TMLR の受理基準 = 「主張が証拠で裏付くか」＋「一部の ML 読者に有益か」。**novelty/impact を問わない**
  → 本論文の強み（事前登録・anti-rescue・決定性 control・provenance）がそのまま加点、
    弱み（控えめ主張・2点）は reject 理由にならない。
- **original 研究可**（ReScience C は特定既存論文の replication 限定で scope 外＝desk reject risk、empirical 確認済）。
- open access（無料）・permanent（journal、ICBINB 等 workshop より被引用/永続性で優位）・rolling 投稿・OpenReview 公開査読。

## 却下した候補
- **ReScience C**: 思想は完全一致だが scope=「出版済み論文の図表を別チームが再実装」。本研究は original study で対象外。
- **ICBINB workshop**: 「意外/負の結果」歓迎で H1 反証は刺さるが、workshop ゆえ permanence 弱。将来の派生短報には可。
- **Sci Rep / PLOS ONE**: 汎用だが significance pushback risk（2点結果）。TMLR の方が Fit。

## 投稿形式の含意（次段）
- TMLR は **LaTeX（tmlr style）+ OpenReview** 投稿。現行の markdown section 群は venue 非依存の content なので、
  最終段で TMLR LaTeX へ組む（sci-rep docx ビルドは不要化）。
- 公開査読（OpenReview）: 事前登録 seal の公開タイムスタンプと相性良（repo public + Zenodo DOI を投稿時に）。

## 残タスク（投稿まで）
1. markdown → TMLR LaTeX 組版（+ refs.bib、図3枚は既に 600dpi+provenance）。
2. bib 著者リスト最終 verify（arXiv 3件 NEEDS-VERIFY）。
3. 投稿時: GitHub repo public 化 + Zenodo DOI + neuro.bin sha256 明記。
4. （任意・査読で要求時）124M 第2backend / 50M same-machine CUDA↔CPU で交絡断ち / H3 multi-seed。
