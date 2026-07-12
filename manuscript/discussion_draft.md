# Discussion

Our central result is that the cross-hardware non-determinism of language-model pretraining
is **not a universal nuisance but an emergent failure mode**: at 10M parameters the same
recipe on CPU, CUDA, and Metal produces essentially one model (0.2% prediction disagreement),
whereas at 50M it produces different models (13.2%) that nonetheless share the same validation
loss. Two design choices give this claim unusual force. Because the study was
pre-registered and sealed, we could not convert a surprising outcome into a claimed
prediction: our persistence hypothesis (H1) was refuted at 10M, and the anti-rescue ledger
prohibited retrofitting the threshold or excising the small-model result. And because
within-machine CPU/CUDA training was verified to be bit-identical, the cross-backend
divergence cannot be dismissed as generic run-to-run noise — it is specifically attributable
to the hardware/numerical path.

**Reconciling the scale effect with prior small-scale observations.** A pilot on an
overfitting toy task (tiny character-level Shakespeare, 0.8M parameters) had shown large
cross-backend disagreement (17–19%). The refutation at 10M is not a contradiction but a
**regime distinction**: the toy task sits in a memorization regime whose sharp loss surface
amplifies tiny numerical differences, whereas our 10M model sits in a generalization regime
on real text where the surface is smoother and differences do not grow. At 50M, added
capacity sharpens the surface again and divergence re-emerges. The disciplined claim is
therefore restricted to a single regime — increasing model size from 10M to 50M on the same
non-overfitting corpus makes divergence emerge — and the toy-task numbers are reported only
as a distinct, corroborating regime rather than folded into the main claim.

**Practical implications.** The combination of H1 and H4 is the actionable message. Model
developers who verify a training pipeline by comparing final loss across machines will see
agreement and conclude the pipeline is portable, while the resulting models may in fact
differ on more than one in ten predictions. As model size grows — the direction the field is
moving — this masked divergence grows rather than shrinks, and reduced-precision training
(H3), now standard, moves its onset dramatically earlier. Reproducible pretraining at scale
therefore requires pinning the hardware and numerical path, not merely the seed and data, and
verifying reproducibility at the level of predictions rather than aggregate loss.

**Limitations.** The 124M model fit only on CUDA, so the cross-backend comparison spans two
sizes; extending it to 124M (e.g., via quantization or gradient accumulation to fit a second
backend) would let us fit an emergence curve rather than a two-point contrast. At 50M the
feasible cross-backend pair (CUDA↔MPS) confounds backend, machine, and CUDA build, though the
within-backend determinism controls and the identical PyTorch version bound this. H3 rests on
a single precision-paired seed. Finally, onset is resolved only at eight milestone steps.
None of these threaten the qualitative result — reproducible at 10M, divergent at 50M with
matched loss — but each is a natural target for a follow-up.

**Outlook.** Beyond closing these gaps, the apparatus itself is a contribution: a sealed
pre-registration, a determinism-controlled harness, an openly licensed corpus with recorded
provenance, and per-run environment fingerprints, all runnable on commodity hardware at no
cost. This lowers the barrier for the community to map *where*, in the space of model size,
precision, and backend, pretraining stops being reproducible — a map that, on the present
evidence, the field cannot assume is empty.
