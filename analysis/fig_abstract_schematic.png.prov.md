# Provenance — fig_abstract_schematic.png

**Created (UTC):** 2026-07-12T01:05:17.939966+00:00

## What this is
Graphical abstract: one training recipe (same seed/data/code) run on CPU/CUDA/MPS produces a near-identical model at 10M params (0.2% prediction disagreement) but divergent 'equally-good-but-different' models at 50M (13.2% disagreement, equal loss). Numbers from the SEALED size-ladder analysis (analysis/ladder_report.md).

## Exact code
- script: `/Users/tadanobukamijo/projects/repro-pretrain/analysis/fig_abstract_schematic.py`
- git: `311f71536865 (main)`

## Environment
- python 3.12.13 on macOS-26.5.2-arm64-arm-64bit
- packages: matplotlib=3.11.0
- requirements.txt sha256[:16]: `None`

## Params / seed
- seed: `None`
- params: `{}`

## History
- decisions/2026-07-11-sizeladder-prereg-SEALED.md

_schema: artifact-provenance/v1_
