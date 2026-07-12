# Paper skeleton — repro-pretrain manuscript

最終更新: 2026-07-12
target venue: Scientific Reports / PLOS ONE / ReScience C / systems-ML methods 系（reproducibility/systems 寛容誌）。出口確定は Discussion 完成後。
grounding: `decisions/2026-07-11-sizeladder-prereg-SEALED.md`（封印仮説）+ `decisions/2026-07-12-sizeladder-results.md`（結果解釈）+ `analysis/ladder_report.md`。

## Working title（3 候補、referee M1 後 = literal を primary に）

1. （primary, defensible）"Same recipe, different model: cross-system reproducibility of byte-level language-model pretraining holds at 10M but fails at 50M parameters" 
2. （punchy, "emergence" は post-hoc 明示前提でのみ）"When does pretraining stop being reproducible? A zero-cost, pre-registered probe of cross-hardware divergence across model size and precision"
3. （method 前面）"A determinism-controlled, open-corpus apparatus for measuring cross-system reproducibility of language-model pretraining"

## Author list（暫定 — 共著は user 確定）

- Tadanobu C. Kamijo (Department of Systems Physiology, Graduate School of Medicine, University of the Ryukyus) — first / corresponding
- （共著候補は user 判断。現状は独立 methods PoC のため single-author 想定でも成立。）

## Keywords（5–7）
reproducibility, numerical determinism, language-model pretraining, hardware heterogeneity, mixed precision, floating-point non-associativity, open corpus

## Structure（Sci Rep standard, build script は rat-voiding `18_build_sci_rep_docx.py` 流用）

| section | target words | 主 content | status |
|---|---:|---|---|
| Title page | — | title / author / affiliation / corresponding | placeholder |
| Abstract (structured) | 200 | Background / Methods / Results / Conclusions | draft（下記）|
| Introduction | 700–900 | (1) 再現性の要請 (2) HW 非決定性の既知だが未測(大規模高コスト) (3) 小型×多数 run の窓 (4) 貢献 | draft |
| Methods | 1,300–1,800 | corpus(OA/permissive) / harness(byte-level GPT, determinism flags) / $0 fleet / pre-registration + anti-rescue / metrics(予測不一致・onset) | draft |
| Results | 1,200–1,600 | 決定性 control / H1 スケール創発 / H2 onset / H3 精度 / H4 loss 隠蔽 | draft |
| Discussion | 1,000–1,400 | 主張(スケール創発) / regime 差(tiny 区別) / 実務含意 / 限界 / future | draft |
| Conclusion | 150–250 | 再掲 + 含意 | placeholder |
| References | — | ~25–35（determinism/reproducibility/FP/nanoGPT/PMC OA）| seed |
| Author Contributions | — | CRediT | placeholder |
| Funding | — | KAKENHI 番号（要 user 確認）| placeholder |
| Competing Interests | — | "The author declares no competing interests." | standard |
| Data & Code Availability | — | GitHub(tckamijo/repro-pretrain 予定) + corpus 再現手順(PMC OA, collect_neuro.py) + neuro.bin sha256 | draft |
| Figures | 3 | (1) graphical abstract schematic (2) H1 scale-emergence (3) H3 precision | 完成(600dpi+provenance) |
| Supplementary | — | full ladder_report.md / run matrix / determinism table / sealed pre-reg | candidate |

## Abstract draft v1（structured, ~205 words）

### Background
Neural-network training is expected to be reproducible: the same recipe — identical seed, data, and code — should yield the same model. In practice, results differ across hardware, but the phenomenon is poorly quantified at scale because repeating large-model pretraining many times is prohibitively expensive. Small models trained many times open a measurement window that has been largely unused.

### Methods
We pretrained byte-level Transformer language models (10M–124M parameters) on a 300 MB permissively licensed (CC-BY/CC0) neuroscience open-access corpus, on a zero-cost heterogeneous fleet spanning an NVIDIA CUDA GPU, an Apple-Silicon Metal (MPS) backend, and CPUs across two machines. We swept seeds, model sizes, and numerical precisions for 4,000 steps. Hypotheses, thresholds, and an anti-rescue ledger were pre-registered and cryptographically sealed before any run. Cross-backend divergence was measured as held-out next-token prediction disagreement; same-seed replicates served as determinism controls.

### Results
Within a machine and backend, CPU and CUDA reproduced bit-identically; MPS was self-non-reproducible (0.07%). Across systems, reproducibility was size-dependent over the two sizes compared: 10M-parameter models agreed (0.2% prediction disagreement) whereas 50M models diverged into different models (13.2% ± 1.0%, three seeds) despite near-identical validation loss (|Δ| = 0.012) — an "equally-good-but-different" outcome that aggregate metrics hide. In single-seed probes, lower precision brought divergence onset earlier (fp16 by ≤ step 50, bf16 by step 400). Our pre-registered persistence hypothesis (≥10% at both sizes) was refuted at 10M; the resulting scale-dependence is reported as a post-hoc, hypothesis-generating observation, not a confirmed law.

### Conclusions
On the two sizes tested, cross-system reproducibility of pretraining held at 10M but failed at 50M, was masked by aggregate loss, and was worsened by low precision; the single divergent point confounds backend with machine and build, so we attribute it to a cross-system difference rather than the numerical path alone. Small-model, many-run studies on open corpora make this failure mode measurable and reproducible, and motivate—without yet confirming—a scale-dependence hypothesis.
