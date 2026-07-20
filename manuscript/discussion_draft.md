# Discussion

Our result is a pre-registered, four-point scaling curve: on the same 300 MB neuroscience
corpus, the same training recipe produces essentially one model at 10M parameters across CPU,
CUDA, and Metal (0.1% prediction disagreement) but different models from 30M upward
(11–14% disagreement) that share the same validation loss. Cross-system divergence **emerges
sharply between 10M and 30M and then saturates** near 11–14% through 75M. Two design choices
make this credible. Because the study was pre-registered and sealed, we could not convert a
surprising outcome into a claimed prediction: our original persistence hypothesis (H1) was
refuted at 10M, and the anti-rescue ledger prohibited moving thresholds or excising results;
the scale-dependence itself was then tested under a **separate pre-registration** (HE1),
prompted by review, and supported. And because within-machine CPU/CUDA training was *verified*
bit-identical, the divergence is not generic run-to-run noise.

**What we do not claim.** We are careful about the boundaries of the claim. The scale-dependence
is now a **pre-registered, four-point result** (HE1 supported), not a two-point post-hoc
narrative — but we still do not claim a *law*: four sizes over one order of magnitude establish
emergence-then-saturation on our corpus and system pair, not a universal exponent, and whether
the plateau holds or moves at larger scale is untested. More importantly, every divergent point
is a **CUDA↔MPS** pair that confounds backend, machine, operating system, and PyTorch platform
build (2.12.1 vs 2.12.1+cu126); the determinism controls exclude run-to-run noise but not these
system axes. We therefore attribute the divergence to a **difference between two compute
systems**, not to the numerical/hardware path *per se* — isolating the latter requires a
same-machine cross-backend comparison, which CPU throughput made infeasible here and which is
the first item of future work. Finally, the **saturation mechanism is unresolved**: why
divergence jumps between 10M and 30M and then plateaus near 11–14% (rather than growing without
bound) is not explained by our data.

**Regime versus scale.** Within the real neuroscience corpus and non-overfitting regime, the
four-point curve is monotone and well-behaved (0.1% → 11.1% → 13.2% → 13.9% at 11M/32M/50M/72M).
The one point that sits *off* this curve is an early overfitting toy pilot
(0.8M-parameter character-level Shakespeare) that diverged by 17–19% — larger than our 11M
real-corpus model. We read this not as non-monotonicity of scale but as a **regime** effect:
in a memorization regime the sharp loss surface amplifies tiny numerical differences, whereas
our generalization-regime models follow the scale curve above. We find this mechanism plausible
but offer **no direct evidence** for it (no curvature, gradient-noise, or overfitting-gap
measurement), so we do not assert it; the toy result is reported only as a distinct,
corroborating regime. Instrumenting loss-surface sharpness across matched regimes — and
explaining the 10M→30M jump and the subsequent plateau — is a concrete next study.

**Practical implication, appropriately bounded.** The combination of H1 and H4 carries the
actionable message. From 30M upward, a developer who validates a pipeline by comparing final
loss across machines would see agreement while the resulting models differ on more than one in
ten predictions. Whether the plateau holds or the masked divergence resumes growing beyond 75M
is untested; but across our four sizes it does not shrink once emerged, and single-seed probes
suggest reduced precision (now standard) brings its onset dramatically earlier. Prudence therefore favors verifying training-pipeline portability at the
level of predictions, not aggregate loss, and pinning the numerical/system path when exact
reproducibility is required.

**Positioning** (see also Related work). That floating-point non-associativity and
non-deterministic kernels make training hardware-dependent is known [goldberg1991; shanmugavelu2024fpna;
zhuang2022; summers2021], and — most relevant to our H4 — prior work on verifiable training
already reports that the same recipe on different GPU architectures can yield similar aggregate
accuracy but substantially different predictions [srivastava2024verifiable]. We therefore do
**not** claim the same-loss/different-predictions phenomenon as novel; our H4 corroborates it on
a different backend set (CPU/CUDA/Metal rather than GPU–GPU) and an open corpus. Our specific,
narrower delta is a **pre-registered, determinism-controlled, prediction-level** measurement of
how cross-system divergence depends on **model size** for **training from scratch** — an axis
these works do not isolate, and one where inference-side evidence points the *other* way
(token-probability nondeterminism reported size-independent from 270M to 12B [fu2026beyond]).
That contrast is itself a reason the training-scale question is worth posing; we pose it and
answer it with a pre-registered four-point curve. The claim is the disciplined, scale-resolved
measurement, not the existence of hardware-induced divergence.

**Limitations.** (i) Four sizes over one order of magnitude (10M–75M) characterize the
cross-system curve; 124M fit only on CUDA, and the plateau's behavior beyond 75M is untested.
(ii) Every divergent point is a CUDA↔MPS pair, singly confounded with machine and build (above).
(iii) H2 and H3 rest on a single seed. (iv) The emergence/saturation mechanism is unmeasured.
(v) Onset is resolved only at eight milestone steps. None threatens the registered qualitative
result — reproducible at 10M, divergent and saturating from 30M with matched loss — but each
bounds how far it can be generalized.

**Outlook.** Beyond closing these gaps (a second backend at 124M via quantization or gradient
accumulation; a same-machine 50M cross-backend pair; multi-seed precision runs; a loss-surface
probe), the apparatus itself is the durable contribution: a sealed pre-registration, a
determinism-controlled harness, an openly licensed corpus with recorded provenance, and per-run
environment fingerprints, all runnable on commodity hardware at no cost — an instrument the
community can use to map where pretraining stops being reproducible.
