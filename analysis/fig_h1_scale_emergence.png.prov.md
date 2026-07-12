# Provenance — fig_h1_scale_emergence.png

**Created (UTC):** 2026-07-12T01:05:17.968880+00:00

## What this is
H1 scale-emergence: cross-backend next-token prediction disagreement vs training step. 10M CUDA<->CPU stays ~0 (final 0.2%, 3-seed); 50M CUDA<->MPS emerges to 13.2%+-1.0% (onset ~step 800). Divergence is scale-dependent, not universal.

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
