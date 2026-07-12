# Discussion

Our literal result is narrow and solid: on the same 300 MB neuroscience corpus, the same
training recipe produces essentially one model at 10M parameters across CPU, CUDA, and Metal
(0.2% prediction disagreement) but two different models at 50M (13.2%) that share the same
validation loss. Two design choices make even this narrow result unusually credible. Because
the study was pre-registered and sealed, we could not convert a surprising outcome into a
claimed prediction: our persistence hypothesis (H1) was refuted at 10M, and the anti-rescue
ledger prohibited moving the threshold or excising the small-model result. And because
within-machine CPU/CUDA training was *verified* bit-identical, the 50M divergence is not
generic run-to-run noise.

**What we do not claim.** We are careful to separate the registered result from the story it
suggests. First, "divergence emerges with model scale" is a claim about a *function* of size;
we have two sizes, so we treat scale-emergence as a **post-hoc, unregistered hypothesis** that
this contrast motivates, not as a demonstrated law. Second, the single divergent point (50M,
CUDA↔MPS) confounds backend, machine, operating system, and PyTorch platform build
(2.12.1 vs 2.12.1+cu126); the determinism controls exclude run-to-run noise but not these
system axes. We therefore attribute the 50M divergence to a **difference between two compute
systems**, not to the numerical/hardware path *per se* — isolating the latter requires a
same-machine cross-backend comparison at 50M, which CPU throughput made infeasible here and
which is the first item of future work.

**Non-monotonicity, and the limits of the regime story.** Across our full size range the
divergence is not monotone: an overfitting toy pilot (0.8M-parameter character-level
Shakespeare) diverged by 17–19%, our 10M real-corpus model by 0.2%, and 50M by 13.2%
(18% → 0.2% → 13.2%). A tempting reconciliation is a *regime* argument — sharp loss surfaces
in the memorization regime amplify tiny numerical differences, smoother generalization
surfaces do not, and added capacity sharpens the surface again. We find this mechanism
plausible but we offer **no direct evidence** for it (no curvature, gradient-noise, or
overfitting-gap measurement), so we do not assert it. The honest present statement is that
divergence is **non-monotone across scale and its mechanism is unresolved**; distinguishing a
genuine scale effect from a regime (overfitting) effect, by instrumenting loss-surface
sharpness across matched regimes, is a concrete next study.

**Practical implication, appropriately bounded.** The combination of H1 and H4 carries the
actionable message. On the two sizes tested, a developer who validates a pipeline by comparing
final loss across machines would see agreement while the resulting models differ on more than
one in ten predictions. Whether this masked divergence continues to grow at larger scale is
untested and should not be assumed from two points; but it does not shrink between our two
sizes, and single-seed probes suggest reduced precision (now standard) brings its onset
dramatically earlier. Prudence therefore favors verifying training-pipeline portability at the
level of predictions, not aggregate loss, and pinning the numerical/system path when exact
reproducibility is required.

**Positioning.** That floating-point non-associativity and non-deterministic kernels make
training results hardware-dependent is known [refs: goldberg1991; zhuang2022; summers2021].
Our intended delta is specific and should be read as such: a **pre-registered,
determinism-controlled, prediction-level (not loss-level)** measurement of how cross-system
divergence changes with model size, on an **openly licensed corpus** with per-run environment
provenance. We do not claim to be first to observe cross-hardware divergence; we claim a
disciplined, reproducible instrument for measuring *where* it becomes behaviorally material,
and a first two-size data point from it.

**Limitations.** (i) Two sizes contribute to the cross-system comparison; 124M fit only on
CUDA. (ii) The 50M pair is singly confounded (above). (iii) H2 and H3 rest on a single seed.
(iv) The regime mechanism is unmeasured. (v) Onset is resolved only at eight milestone steps.
None threatens the registered qualitative result — reproducible at 10M, divergent at 50M with
matched loss — but each bounds how far it can be generalized.

**Outlook.** Beyond closing these gaps (a second backend at 124M via quantization or gradient
accumulation; a same-machine 50M cross-backend pair; multi-seed precision runs; a loss-surface
probe), the apparatus itself is the durable contribution: a sealed pre-registration, a
determinism-controlled harness, an openly licensed corpus with recorded provenance, and per-run
environment fingerprints, all runnable on commodity hardware at no cost — an instrument the
community can use to map where pretraining stops being reproducible.
