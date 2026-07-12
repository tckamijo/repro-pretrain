# AI 利用開示文（Statement on the use of AI tools）

> ⚠️ **この開示文は、著者が `VERIFICATION_WORKSHEET.md` を完了して初めて正確になる**（"verified by the author"
> の部分）。ワークシートのチェックが全部付く前に投稿しないこと。範囲を盛らない・削らない、事実どおりに。

## 論文に入れる版（"Statement on the use of AI tools" 節、または Acknowledgements 末尾）

> **Statement on the use of AI tools.** In preparing this work the author used a large language
> model (Anthropic's Claude) as an assistive tool. Its role included drafting and editing the
> manuscript text; writing and scaffolding the data-collection, training-harness, analysis, and
> figure-generation code; assisting with the literature search; and running an internal
> adversarial review to surface weaknesses. All experiments were executed by the author on the
> author's own hardware, and every reported quantitative result was produced by the analysis
> code and independently verified by the author against the raw per-run outputs (a
> claim-to-source verification worksheet is included in the repository). The author designed the
> study, sealed the pre-registration, checked all numbers, claims, and citations, and takes full
> responsibility for the content and its scientific validity. No data, results, or citations were
> fabricated: every reported number traces to a recorded run output, and every reference is a
> real source the author verified.

## arXiv / TMLR の開示欄向け（短縮版）

> The author used an LLM (Claude) to assist with code, analysis scaffolding, figure generation,
> literature search, and manuscript drafting/editing. All experiments were run by the author;
> all results, claims, and citations were verified by the author against primary sources and raw
> outputs; the author takes full responsibility. See the repository's verification worksheet.

## メモ（なぜこの形か）
- arXiv 2026-05 ポリシーが罰するのは「**丸投げ＋著者未検証**」。開示 + 実検証（ワークシート）+ 責任表明で、
  「ツールとしての LLM 利用（許容）」の側に立つ。
- TMLR も LLM 支援を開示前提で許容。二重投稿ではなく preprint 併存も許容。
- **虚偽記載しない**: 「軽微な補助」等に矮小化せず、drafting を含む実際の範囲を書く。正直さ自体が防御。
- 開示文はリポジトリにも置く（透明性）。`VERIFICATION_WORKSHEET.md` と対で機能する。
