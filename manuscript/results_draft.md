# Results

We trained 27 models to 4,000 steps each (Mac: 11; NVIDIA host: 16), all recording the
expected PyTorch version and full eight-point milestone curves. Results are reported against
the sealed thresholds.

## Determinism controls hold; MPS is the exception

Same-machine, same-backend, same-seed replicates were **bit-identical** on both the CPU and
the CUDA backends (weight SHA-256 match; 0.00% prediction disagreement at step 4,000),
confirming that our harness is deterministic enough for cross-backend differences to be
attributable. The **Metal (MPS) backend was self-non-reproducible**: two identical-seed runs
disagreed on 0.07% of predictions and produced different weight fingerprints, matching the
pre-registered expectation that MPS is not bit-reproducible even on fixed hardware and seed.
Cross-backend differences below are therefore interpreted against a CPU/CUDA baseline that is
itself exactly reproducible.

## H1: cross-backend divergence emerges with scale (persistence hypothesis refuted)

At **10M parameters**, all six cross-backend/cross-machine pairs agreed almost completely:
CUDA↔CPU disagreement was **0.2%** (three seeds), and every other pair (CPU↔CPU across the
two machines, CUDA↔MPS, MPS↔CPU, etc.) fell between 0.1% and 0.2% — squarely in the
pre-registered **washed-out** band (<5%). At **50M parameters**, the feasible cross-backend
pair (CUDA↔MPS) disagreed on **13.2% ± 1.0%** of predictions (three seeds) — in the
**supported** band (≥10%) (Fig. 2). The sealed **H1**, which required ≥10% at *both* sizes,
is therefore **refuted as stated**: divergence is not persistent across scale but **emerges
between 10M and 50M**. Because both sizes share the same corpus and non-overfitting regime,
this is a clean within-regime scale effect rather than an artifact of the metric.

## H2: onset consistent with the emergence direction

Tracking disagreement across training steps, the 10M CUDA↔CPU pair never crossed the 1%
onset threshold (final 0.3%), whereas the 50M CUDA↔MPS pair crossed it by **step 800** and
plateaued near 11–13% (Fig. 2). With only one size exhibiting divergence, we cannot fit an
onset-versus-size trend, but the direction — the larger model diverges while the smaller does
not — is consistent with the pre-registered H2.

## H3: low precision brings divergence earlier (supported)

Holding the CUDA backend and seed fixed at 50M, we compared fp32 against reduced precision
(Fig. 3). Divergence from the fp32 reference appeared far earlier and grew far larger at
lower precision: **fp32↔bf16** crossed the 1% onset by **step 400** (final 13.6%), and
**fp32↔fp16** already disagreed on 6.4% of predictions by **step 50** and reached **71.9%**
by step 4,000. Lower precision thus brings the onset of divergence hundreds to thousands of
steps earlier and amplifies its magnitude, supporting **H3**.

## H4: aggregate loss masks the divergence (supported)

For the 50M CUDA↔MPS pair that disagreed on 13.2% of predictions, the corresponding
validation-loss difference was only **|Δ| = 0.012** — below the pre-registered 0.05 masking
threshold. The two backends therefore produced models that are **equally good by validation
loss yet behaviorally different**, supporting **H4**: a scalar aggregate metric conceals the
hardware-induced divergence that a prediction-level comparison reveals.

## Summary

Within a machine and backend, CPU and CUDA training is exactly reproducible and MPS is not;
across backends, models are reproducible at 10M but diverge at 50M despite matched loss; and
reduced precision moves this divergence dramatically earlier. Of the four pre-registered
hypotheses, H3 and H4 were supported, H2 was directionally consistent, and H1 was refuted in
a way that sharpened rather than weakened the central claim (Discussion).
