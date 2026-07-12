# Related work and positioning

(Intended to fold into the Introduction's middle and to replace the Discussion "Positioning"
paragraph. Written after a literature search; the honest delta is narrower than an early draft
implied — the *phenomenon* is known, our contribution is a pre-registered, scale-resolved,
open-corpus measurement of it.)

**Floating-point non-associativity and numerical reproducibility.** That summation order
changes floating-point results is textbook [goldberg1991], and its consequences for HPC and
deep-learning reproducibility have been characterized directly [shanmugavelu2024fpna]. Parallel GPU
reductions, kernel non-invariance, and batch-size effects are established implementation-level
sources of run-to-run and cross-device variance [shanmugavelu2024fpna; pytorch_repro; nvidia_determinism].
We do not re-establish these; we take them as the mechanism and ask a downstream question.

**Hardware nondeterminism yields behaviorally different models at matched aggregate
performance.** Most directly related to our H4, prior work on verifiable training shows that the
*same* recipe on *different GPU architectures* can produce models with similar aggregate
accuracy yet substantially different predictions, and treats this as an obstacle to be
controlled [srivastava2024verifiable]. Related analyses characterize numerical sources of
nondeterminism in LLM inference at temperature zero [yuan2025llminfer], and optimization-level
work documents instability and nondeterminism during training [summers2021; zhuang2022]. Our
H4 result — 13.2% prediction disagreement at near-identical validation loss — therefore
**corroborates**, on a different backend set (CPU/CUDA/Metal rather than GPU–GPU) and an open
corpus, a phenomenon these works already report; we do not claim it as novel.

**Variance and reproducibility methodology in ML.** A methodological literature argues for
treating training variance as a first-class quantity and for reporting it across seeds and
tooling [bouthillier2021; henderson2018; pineau2021]. We adopt that stance and add
pre-registration with an anti-rescue ledger, which is uncommon in this systems-ML setting.

**Precision.** Reduced-precision training is known to be less numerically stable, with fp32
near-deterministic and bf16/fp16 more variable [shanmugavelu2024fpna; yuan2025llminfer]; our single-seed H3
probe is consistent in direction (lower precision → earlier onset) and is offered as
corroboration rather than a controlled precision study.

**Our delta (one sentence per axis).** Relative to the above: (i) we measure how cross-system
divergence depends on **model size** (a scale axis these works do not isolate), finding it
washed out at 10M and material at 50M; (ii) we do so under a **sealed pre-registration** with an
anti-rescue ledger, so a refuted hypothesis is reported as refuted; (iii) we compare at the
level of **held-out predictions** with same-seed **bit-identity controls**, not aggregate loss
alone; and (iv) we release an **openly licensed corpus** and per-run environment provenance so
the measurement is exactly re-runnable on commodity hardware. The novelty is the disciplined,
scale-resolved *instrument and measurement*, not the existence of hardware-induced divergence.
