# Results

We trained 27 models to 4,000 steps each (Mac: 11; NVIDIA host: 16), all recording the
expected PyTorch build and full eight-point milestone curves. Results are reported against
the sealed thresholds. Unless stated otherwise, cross-backend disagreement is the three-seed
mean; onset and precision traces (H2, H3) are **single-seed (seed 0)** and are labelled as
such throughout.

## Determinism controls hold; MPS is the exception

Same-machine, same-backend, same-seed replicates were **bit-identical** on both the CPU and
the CUDA backends (weight SHA-256 match; 0.00% prediction disagreement at step 4,000). We
confirmed this empirically rather than assuming it: despite the CUDA memory-efficient-attention
non-determinism warning, two seed-0 CUDA runs produced identical weight fingerprints, so
deterministic kernels were **achieved**, not merely requested. The **Metal (MPS) backend was
self-non-reproducible**: two identical-seed runs disagreed on 0.07% of predictions with
different weight fingerprints, matching the pre-registered expectation. Cross-backend
differences below are therefore read against a CPU/CUDA baseline that is itself exactly
reproducible.

## H1: divergence emerges with scale, then saturates (persistence refuted; scale-dependence pre-registered and supported)

At **10M parameters**, all six cross-backend/cross-machine pairs agreed almost completely:
CUDA↔CPU disagreement was **0.2%** (three seeds), and every other pair (CPU↔CPU across the two
machines, CUDA↔MPS, MPS↔CPU) fell between 0.1% and 0.2% — in the pre-registered **washed-out**
band (<5%). At **50M**, the feasible cross-backend pair, **CUDA↔MPS**, disagreed on
**13.2% ± 1.0%** of predictions (mean ± SD over seeds {0,1,2}) — in the **supported** band
(≥10%). The original sealed **H1**, which required ≥10% at *both* sizes, is therefore **refuted
as stated**: reproducibility is not uniform but size-dependent.

Because two sizes cannot characterize a function of scale, we **pre-registered a second,
denser experiment** (prompted by peer review; sealed before running, commit 3bff416) adding
**30M** and **75M** models and predicting (HE1) that CUDA↔MPS disagreement increases with size
across 10M/30M/50M/75M. The four-point CUDA↔MPS curve (three seeds each) is
**0.1% → 11.1% ± 2.3% → 13.2% ± 1.0% → 13.9% ± 0.4%** (10.9M / 31.9M / 49.7M / 72.0M
parameters; Fig. 2). **HE1 is supported** (weakly monotonic, 75M ≥ 50M), and the curve reveals
a **shape two points could not**: divergence **emerges sharply between 10M and 30M**
(0.1% → 11.1%, crossing the 10% band) and then **saturates** near 11–14% from 30M to 75M
(sub-linear). The per-step traces (Fig. 2, right) show 10M stays flat throughout training while
the larger models cross onset by step 400–800. We note the 30M point is the least stable
(±2.3%; one seed at 8.0%), consistent with its position at the transition edge; 50M and 75M are
tight (±1.0%, ±0.4%). This scale-dependence is thus a **pre-registered, supported** finding, not
a post-hoc narrative — though the divergent points remain CUDA↔MPS pairs that confound backend
with machine and PyTorch build, and the saturation mechanism is unresolved (see Discussion).

## H2: onset present at 50M, absent at 10M (single-seed)

Tracking seed-0 disagreement across steps, the 10M CUDA↔CPU pair never crossed the 1% onset
threshold (final 0.3%). The 50M CUDA↔MPS pair crossed 1% by **step 800** (9.2%) and first
reached the ≥10% band by **step 1,600**; thereafter it fluctuated non-monotonically between
about 9% and 12% (12.3 → 10.8 → 11.9% at steps 1,600/3,200/4,000) rather than climbing
smoothly (Fig. 2). With only one size exhibiting any divergence and a single seed, we cannot
fit an onset-versus-size relationship; the direction (larger diverges, smaller does not) is
merely consistent with the pre-registered H2.

## H3: lower precision brings divergence earlier (supported, single-seed)

Holding the CUDA backend and seed (0) fixed at 50M, we compared fp32 against reduced precision
(Fig. 3). Divergence from the fp32 reference appeared earlier and larger at lower precision:
**fp32↔bf16** crossed the 1% onset by **step 400**, and **fp32↔fp16** already disagreed on 6.4%
of predictions by **step 50** — i.e. its onset is at or before our first milestone (≤ step 50),
below the resolution of the grid. The fp16 trace is itself strongly non-monotone
(51.8 → 45.1 → 25.7 → 71.9% at steps 400/800/1,600/4,000); we therefore report the direction
(low precision → earlier, larger divergence) as supporting **H3** but treat the specific
endpoint magnitudes, including the 71.9% value, as single-seed and not robust. Additional seeds
for the precision axis are pre-registered future work.

## H4: aggregate loss masks the divergence (supported)

For the 50M CUDA↔MPS pair that disagreed on 13.2% of predictions, the corresponding
validation-loss difference was only **|Δ| = 0.012** — below the pre-registered 0.05 masking
threshold. The two backends produced models that are **equally good by validation loss yet
behaviorally different**, supporting **H4**: a scalar aggregate metric conceals the
cross-system divergence that a prediction-level comparison reveals. This corroborates, on a
CPU/CUDA/Metal backend set and an open corpus, the same-accuracy/different-prediction effect
reported for GPU architectures by prior verifiable-training work [srivastava2024verifiable]; we
do not claim it as novel (see Discussion).

## Summary

Within a machine and backend, CPU and CUDA training is exactly reproducible and MPS is not;
across systems, models are reproducible at 10M but diverge at 50M despite matched loss; and,
in single-seed probes, reduced precision moves divergence earlier. Of the four pre-registered
hypotheses, H3 and H4 were supported, H2 was directionally consistent, and H1 was refuted. We
report the refutation as a refutation; the scale-dependence it exposes is developed in the
Discussion as a hypothesis for future, adequately-powered work, not as an established result.
