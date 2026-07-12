# Referee Report #1 (paper-reviewer, 2026-07-12) — pre-submission adversarial review

Verdict: **Major revision.** Process hygiene top-decile (sealed pre-reg, honored ledger,
bit-exact controls, every number traces to raw, provenance sidecars). Vulnerability is in
**framing**: a two-point (10M/50M), singly-confounded (50M=CUDA↔MPS), partly single-seed
(H2/H3) result is narrated as an "emergence" law with a settled mechanism. Closable by
reframing + honest hedging, not new experiments.

## Major (blocking)
- **M1** "Emergence" from N=2 sizes (one with N=1 cross-backend pair). → demote "emergent" to
  literal "reproducible at 10M, divergent at 50M"; reserve emergence for explicit speculation;
  or add a 2nd backend at 124M for ≥3 points.
- **M2** The one divergent point (50M, 13.2%) confounds backend × machine × CUDA build ×
  PyTorch build. Determinism control rules out run-to-run noise but NOT machine/OS/build. →
  soften "hardware/numerical path" to "cross-system"; or break confound (same-machine
  CUDA↔CPU at 50M reduced steps, or same-box 2nd backend).
- **M3** Refuted-H1 → "scale emergence" reframe presented as *strengthening*. Ledger-clean, but
  the reframe is **new & unregistered**. → label scale-dependence as post-hoc /
  hypothesis-generating; pre-registration credits the *refutation*, not the reframe.
- **M4** tiny-Shakespeare "regime distinction" is an untested just-so story; full range is
  non-monotone 18%→0.2%→13.2%. → measure a mechanism proxy (loss curvature / grad variance /
  train-val gap) OR downgrade to "cannot distinguish scale from regime; non-monotone; mechanism
  unresolved."
- **M5** Novelty under-defended; no .bib exists; FP-nonassociativity is known. → write real
  related-work with one-sentence delta vs closest papers; produce the bib; the novel delta is
  "pre-registered, determinism-controlled, prediction-level (not loss-level) scaling of
  cross-backend divergence on an open corpus."
- **M6** H2/H3 onset traces are single-seed (s0); text implies 3-seed rigor. → label n=1 on
  every onset/precision number; caveat/drop the 71.9% fp16 endpoint (single-seed, non-monotone
  400:51.8→800:45.1→1600:25.7→4000:71.9); add 2 seeds for H3 if possible.

## Minor
- **m1** 50M "plateaued 11–13%" smooths non-monotone 9.2→12.3→10.8→11.9; onset (>1%) at 800 but
  ≥10% band only at 1600. **m2** "identical PyTorch 2.12.1" contradicts 2.12.1 vs 2.12.1+cu126 →
  "same release, different platform builds." **m3** verify PyTorch 2.12.1 is a real release (flag
  if nightly/internal). **m4** CC-BY-SA listed as kept but absent in corpus → "permitted but not
  present." **m5** give all arch hyperparams for all 3 sizes in a table (50M heads missing; 124M
  unconventional). **m6** clarify deterministic CUDA kernels were *achieved* not just requested.
  **m7** fp16 onset is ≤ step 50 (6.4% already at 50; grid can't resolve). **m8** "masked
  divergence grows with size" is a 2-point extrapolation stated as fact → hedge. **m9** add figure
  legends; define error bar (±1.0% = SD over seeds {0,1,2}); Fig.1 never called out in body.
  **m10** repo/DOI must be live+archived at submission (reproducibility paper).

## Checks passed
Run count 27 recomputed ✓. All headline numbers trace to raw, no fabrication ✓. Pre-registration
integrity exemplary ✓. Determinism controls pass ✓. Confound control FAIL for headline (M2).
Citation bidirectional check impossible (no bib, M5).

Full report archived from paper-reviewer agent run 2026-07-12.
