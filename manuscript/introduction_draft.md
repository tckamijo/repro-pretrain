# Introduction

Reproducibility is a load-bearing assumption of computational science: an independent
re-execution of the same procedure should reproduce the same result. For neural-network
training this assumption is routinely invoked when a "model" is treated as a deterministic
function of its recipe — the training data, the random seed, the code, and the
hyperparameters. In practice, however, the mapping from recipe to trained weights also
passes through a hardware- and library-specific numerical path, and that path is not
bit-neutral. Floating-point addition is not associative, reduction orders differ between
CPU, GPU, and accelerator kernels, and several high-performance kernels are non-deterministic
by default [goldberg1991; pytorch_repro; nvidia_determinism]. The practical
question is not whether such differences exist but whether they matter — whether they stay
in the numerical noise floor or grow into behaviorally different models.

This question is under-measured precisely where it matters most. Characterizing run-to-run
and cross-hardware variability requires training the same configuration many times, but at
the scale of contemporary language models a single pretraining run can cost thousands of
GPU-hours, so repetition is rare and variability is usually reported, if at all, as a single
seed's loss curve [bouthillier2021; kaplan2020]. The measurement window that *is*
affordable — small models trained many times, across heterogeneous hardware — has been
largely unused. Small models are not merely cheap stand-ins; because the same numerical
non-associativity operates at every scale, they let us ask a sharper question: *as a model
grows, does cross-hardware divergence stay negligible, or does it emerge?*

We approach this with three deliberate design choices. First, the study is **pre-registered**:
the hypotheses, decision thresholds, feasibility caveats, and an explicit anti-rescue ledger
were written and cryptographically sealed before any full run, so that a surprising result
cannot be retrofitted into a confirmed prediction. Second, it is **zero-cost**: all training
runs on a small heterogeneous fleet already on hand — an NVIDIA consumer GPU (CUDA), an
Apple-Silicon machine (Metal/MPS), and CPUs on two different microarchitectures — so the
heterogeneity that is usually a nuisance becomes the independent variable. Third, it is
demonstrated on an **open, permissively licensed domain corpus**: roughly 300 MB of
CC-BY/CC0 neuroscience open-access full text, so that both the corpus and the resulting
artifacts can be released for exact re-derivation.

Our contribution is threefold. (i) With pre-registered thresholds and three-seed error bars,
we measure cross-system divergence in byte-level language-model pretraining across **four model
sizes** (10M–75M) and find it **strongly size-dependent**: negligible at 10M (0.1% prediction
disagreement), it **emerges sharply between 10M and 30M** (to 11.1%) and then **saturates**
near 11–14% through 75M. The monotone scale-dependence was itself pre-registered (in a second
sealed experiment prompted by review) and supported. (ii) We show this divergence is **hidden by aggregate
metrics** — models disagreeing on 13% of held-out next-token predictions can have
near-identical validation loss — and that, in single-seed probes, it is **worsened by low
precision**, with bf16 and fp16 bringing onset hundreds to thousands of steps earlier.
(iii) We provide a **reproducibility apparatus** — a sealed pre-registration with an
anti-rescue ledger, a determinism-controlled harness, an openly licensed corpus with recorded
provenance, and per-run environment fingerprints — that makes the phenomenon measurable on
commodity hardware and directly re-runnable by others.
