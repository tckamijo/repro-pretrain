# Response to Referee Report #1 (2026-07-12)

We thank the reviewer. The core message — process hygiene is strong but the framing outran a
two-point, singly-confounded, partly single-seed result — is correct, and we have revised the
framing accordingly (reframing + hedging, no fabricated experiments). Point-by-point:

## Major
- **M1 (emergence from N=2)** — DONE (reframe). "Emergent" demoted throughout to the literal
  "reproducible at 10M, divergent at 50M." Abstract, Intro (i), Results §H1, and title all now
  state a two-point contrast and explicitly label scale-emergence as a hypothesis two sizes
  cannot confirm. Adding a 2nd backend at 124M is listed as future work.
- **M2 (50M confound)** — DONE (soften) + FUTURE (break). Attribution changed from
  "hardware/numerical path" to "a difference between two compute systems (backend + machine +
  build)" wherever the 50M result is invoked (Abstract, Results §H1, Discussion). A
  same-machine CUDA↔CPU 50M comparison to break the confound is the first future-work item.
- **M3 (refute→reframe as strengthening)** — DONE. Removed all "stronger/sharpened" rhetoric.
  Now: the pre-registration credits the *refutation*; the scale-dependence is a **post-hoc,
  unregistered, hypothesis-generating** observation (stated in Abstract, Results §H1,
  Discussion "What we do not claim").
- **M4 (regime just-so + non-monotonicity)** — DONE (downgrade). We now state the full range is
  **non-monotone (18% → 0.2% → 13.2%)**, present the regime mechanism as *plausible but
  unevidenced*, and say the mechanism is **unresolved**; instrumenting loss-surface sharpness is
  named as the deciding future study.
- **M5 (novelty / no bib)** — DONE. Ran a literature search and wrote `related_work_draft.md`
  with a one-sentence delta per axis. Crucially, the search found that our H4
  (same-loss/different-predictions) is **not novel** — prior verifiable-training work reports it
  for GPU architectures [srivastava2024verifiable, arXiv:2403.09603]; we now explicitly frame H4
  as corroboration on a new backend set/open corpus, not a discovery. Compiled `refs.bib` with
  real works (arXiv IDs from the search; author lists marked NEEDS-VERIFY where not confirmed —
  no names invented). The narrowed, honest delta is the pre-registered, scale-resolved,
  open-corpus *instrument and measurement*. A deeper prior-art sweep (2026-07-12) added three
  directly-adjacent works and sharpened positioning: inference-side nondeterminism was found
  *size-independent* from 270M to 12B [fu2026beyond], so we now frame our training-from-scratch
  size-dependence as a two-point *first probe* and an open training-vs-inference contrast, not a
  trend; deployment cross-backend drift [li2025crossbackend] and the training-reproducibility
  taxonomy [chen2022trainrepro] are engaged and distinguished. The specific combination is not scooped.
- **M6 (single-seed H2/H3)** — DONE (label) + FUTURE (seeds). Every onset/precision number is
  now labelled single-seed (seed 0). The 71.9% fp16 endpoint is explicitly called single-seed,
  non-monotone, and not robust, and removed as an abstract headline. Extra precision-axis seeds
  are pre-registered future work.

## Minor
- **m1** fixed: "fluctuated non-monotonically ~9–12%"; onset at 800, ≥10% band only at 1600.
- **m2** fixed: "same release, different platform builds (2.12.1 vs 2.12.1+cu126)."
- **m3** PyTorch 2.12.1 is the real installed build in our environment; recorded in every run
  JSON. (Noted for reviewers; not altered.)
- **m4** fixed: CC-BY-SA "permitted by the gate but none appeared."
- **m5** fixed: full hyperparameter table for all three sizes; noted 124M ≠ GPT-2 124M config.
- **m6** fixed: state deterministic CUDA kernels were *achieved* (empirically bit-identical),
  not merely requested.
- **m7** fixed: fp16 onset "≤ step 50."
- **m8** fixed: "grows with size" hedged to "does not shrink between our two sizes; larger scale
  untested."
- **m9** DONE: figure legends added (`figures_plan.md`); error bar defined = ±1 SD over seeds
  {0,1,2}; Fig. 1 noted as standalone graphical abstract.
- **m10** acknowledged: GitHub repo + Zenodo DOI + neuro.bin sha256 + sealed pre-reg to be made
  live/archived at submission (currently private repo; the reproducibility deliverable).

## Net
No new empirical claims were added and no thresholds moved; the revision only *reduces* claim
strength to match the evidence and labels the post-hoc reframe as such — consistent with the
sealed anti-rescue ledger. Remaining substantive TODO before submission: (1) related-work +
compiled bib (M5), (2) live archived repo/DOI (m10), and the optional confound-breaking /
multi-seed experiments (M1, M2, M6) if the venue requires ≥3 points.
