# Provenance — fig_h1_scale_emergence.png

**Created (UTC):** 2026-07-20T02:24:37.781125+00:00

## What this is
H1 scale curve (pre-registered extension): CUDA<->MPS next-token prediction disagreement vs model size, 4 points 10.9/31.9/49.7/72.0M = 0.1/11.1/13.2/13.9% (3-seed). Divergence emerges sharply between 10M and 30M then saturates ~11-14%. Right panel: per-step onset (seed 0), 11M flat vs larger models crossing onset by step 400-800.

## Exact code
- script: `/Users/tadanobukamijo/projects/repro-pretrain/analysis/plot_ladder.py`
- git: `608df559c6c1+dirty (main)`

## Environment
- python 3.12.13 on macOS-26.5.2-arm64-arm-64bit
- packages: numpy=2.5.1, matplotlib=3.11.0
- requirements.txt sha256[:16]: `None`

## Params / seed
- seed: `None`
- params: `{}`

## History
- decisions/2026-07-20-ladder-extension-results.md

_schema: artifact-provenance/v1_
