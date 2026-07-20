# Methods

## Corpus

We built a domain corpus from the NCBI PubMed Central (PMC) Open Access subset via the
E-utilities API (`esearch`/`efetch`), restricted to neuroscience full text. Because the
`open access[filter]` still admits non-commercial and no-derivatives licenses, every article
was gated on its JATS `<license>` element and **only permissive licenses were kept — CC0,
CC-BY, and CC-BY-SA** (CC-BY-SA was permitted by the gate but none appeared in the final
corpus) — with all rejections logged for auditability. Article bodies were
extracted from the JATS XML (tables, figures, reference lists, and mathematics removed),
concatenated in ascending PMCID order with a document separator, and stored as a raw
byte stream. The final corpus is 300.12 MB (6,961 documents: 6,933 CC-BY, 28 CC0; zero
NC/ND contamination) with recorded SHA-256, split 99.5/0.5 into train and validation. The
collector is stdlib-only and rate-limited to NCBI's guidance (≤3 requests/s). Corpus
assembly is deterministic, so the byte stream is reproducible from the document set.

## Model and training harness

Models are byte-level (vocabulary 256) decoder-only Transformers. Three size presets were
used; the preset names (10M/50M/124M) are nominal size-class labels, and the actual parameter
counts are given below (all hyperparameters are stated for exact reproducibility):

| preset (nominal) | d_model | layers | heads | block (context) | actual params |
|---|---:|---:|---:|---:|---:|
| 10M | 384 | 6 | 6 | 256 | 10.9M |
| 30M | 512 | 10 | 8 | 256 | 31.9M |
| 50M | 640 | 10 | 10 | 256 | 49.7M |
| 75M | 704 | 12 | 11 | 256 | 72.0M |
| 124M | 768 | 16 | 12 | 512 | 114.2M |

(The "124M" label follows the GPT-2 naming convention but is not an exact GPT-2 configuration;
our preset has 114.2M parameters. All comparisons use the actual models above.) Training used
AdamW (lr 3e-4), batch 16, gradient
clipping 1.0, and a fixed data-sampling order independent of the model seed, for 4,000 steps.
The harness records, at eight milestone steps (50, 100, 200, 400, 800, 1,600, 3,200, 4,000),
the validation loss, the argmax next-token predictions on a fixed 4,096-token held-out probe,
a SHA-256 fingerprint of all weights, and per-parameter statistics. Every run's output JSON
records the exact PyTorch version, so any accidental interpreter mismatch is self-evident.

Determinism was requested via `torch.use_deterministic_algorithms`, `cudnn.deterministic`,
and `CUBLAS_WORKSPACE_CONFIG` (set before the framework import). We note that CUDA
memory-efficient attention warns that it is non-deterministic; we therefore treated
within-machine, within-backend bit-identity as an empirical control to be verified rather
than assumed (see Results).

## Heterogeneous fleet

All computation used hardware already on hand at no marginal cost: an NVIDIA GeForce RTX 3060
(CUDA 12.6, driver 560.94; Windows) providing the CUDA backend and an AMD-based CPU; and an
Apple-Silicon Mac mini (macOS) providing the Metal Performance Shaders (MPS) backend and an
ARM CPU. Both machines ran the same PyTorch release (2.12.1) but necessarily
different platform builds — `2.12.1` (Apple/MPS) versus `2.12.1+cu126` (CUDA) — a difference
we treat as part of the cross-system confound rather than claim away as "identical." Feasibility was hardware-bounded and reported honestly: the 124M model fit only
on CUDA (MPS exhausted 16 GB unified memory; CPU was too slow for 4,000 steps), so the
cross-backend comparison spans 10M and 50M, with 124M contributing within-backend controls.

## Pre-registration and anti-rescue

Before any full run, we sealed a pre-registration document (hypotheses H1–H4, decision
bands, feasibility caveats, and a seven-item anti-rescue ledger) by committing it with its
own SHA-256 recorded in the commit message, establishing a time-gate. The ledger explicitly
forbade, among other moves, shifting thresholds to fit results, dropping disagreeing seeds,
extending training until divergence appeared, and re-scoping hypotheses post hoc. All
verdicts below are reported against the sealed thresholds without modification.

## Divergence metric and hypotheses

Cross-backend divergence between two runs is the percentage of the 4,096 fixed-probe
positions at which their argmax next-token predictions differ, at a given step; the
final-step value is the primary outcome and is averaged over seeds {0, 1, 2}. The
pre-registered hypotheses were: **H1 (persistence)** — CUDA↔CPU final disagreement ≥10% at
both 10M and 50M (three-band verdict: ≥10% supported / 5–10% diminished-but-survives / <5%
washed out); **H2 (onset)** — the step at which divergence exceeds 1% moves earlier with
model size; **H3 (precision)** — bf16/fp16 reach onset earlier than fp32; and **H4 (loss
masking)** — models differing by ≥10% in predictions differ by <0.05 in validation loss.
Because 50M has no feasible CPU run, its cross-backend pair is CUDA↔MPS, a substitution
recorded at seal time. The determinism control required same-machine, same-backend,
same-seed replicates to be bit-identical (with MPS self-non-reproducibility a documented
expected exception).
