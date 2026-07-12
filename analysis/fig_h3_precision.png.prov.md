# Provenance — fig_h3_precision.png

**Created (UTC):** 2026-07-12T01:05:17.984673+00:00

## What this is
H3 precision: 50M CUDA fp32 vs bf16/fp16 prediction disagreement vs step. fp16 diverges from fp32 by step 50 (final 71.9%), bf16 by step 400 (final 13.6%); lower precision brings divergence onset earlier. fp32 CUDA<->MPS shown as reference.

## Exact code
- script: `/Users/tadanobukamijo/projects/repro-pretrain/analysis/plot_ladder.py`
- git: `311f71536865+dirty (main)`

## Environment
- python 3.12.13 on macOS-26.5.2-arm64-arm-64bit
- packages: numpy=2.5.1, matplotlib=3.11.0
- requirements.txt sha256[:16]: `None`

## Params / seed
- seed: `None`
- params: `{}`

## History
- decisions/2026-07-11-sizeladder-prereg-SEALED.md

_schema: artifact-provenance/v1_
