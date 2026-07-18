#!/usr/bin/env python3
"""Assemble the TMLR LaTeX submission from the markdown section drafts and build a PDF.

- pandoc converts each section body (markdown -> latex).
- bracketed citation groups [k1; k2] are rewritten to \\citep{k1,k2} ONLY when every
  token is a real refs.bib key (so "[filter]" and similar are left untouched).
- assembles main.tex with the TMLR preamble (preprint mode) + figures + bibliography.
- builds with tectonic (bundles biber; no system TeX needed).

Run from manuscript/latex/.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MS = os.path.dirname(HERE)                      # manuscript/
BIB = os.path.join(MS, "refs.bib")

BIB_KEYS = set(re.findall(r"^@[a-z]+\{([a-z0-9_]+)", open(BIB).read(), re.M | re.I))

TITLE = ("Same recipe, different model: cross-system reproducibility of byte-level "
         "language-model pretraining holds at 10M but fails at 50M parameters")
AUTHOR = (r"Tadanobu Chuyo Kamijo\\"
          r"Department of Systems Physiology, Graduate School of Medicine\\"
          r"University of the Ryukyus, Okinawa, Japan\\"
          r"\texttt{tadanobu@cs.u-ryukyu.ac.jp} \quad ORCID: 0000-0001-6587-7231")

# anonymous (TMLR double-blind submission) vs de-anonymized (arXiv preprint)
ANON = ("--anon" in sys.argv)
PKG_OPT = "" if ANON else "[preprint]"
OUT_PDF = "main_anon" if ANON else "main"

ABSTRACT = (
    "Neural-network training is expected to be reproducible: the same recipe---identical "
    "seed, data, and code---should yield the same model. In practice, results differ across "
    "hardware, but the phenomenon is poorly quantified at scale because repeating large-model "
    "pretraining many times is prohibitively expensive. We pretrained byte-level Transformer "
    "language models (10M--124M parameters) on a 300\\,MB permissively licensed (CC-BY/CC0) "
    "neuroscience open-access corpus, on a zero-cost heterogeneous fleet spanning an NVIDIA "
    "CUDA GPU, an Apple-Silicon Metal (MPS) backend, and CPUs across two machines, sweeping "
    "seeds, model sizes, and numerical precisions for 4{,}000 steps. Hypotheses, thresholds, "
    "and an anti-rescue ledger were cryptographically sealed before any run; cross-backend "
    "divergence was measured as held-out next-token prediction disagreement, with same-seed "
    "replicates as determinism controls. Within a machine and backend, CPU and CUDA reproduced "
    "bit-identically while MPS was self-non-reproducible (0.07\\%). Across systems, "
    "reproducibility was size-dependent over the two sizes compared: 10M models agreed (0.2\\% "
    "prediction disagreement) whereas 50M models diverged into different models "
    "(13.2\\%\\,$\\pm$\\,1.0\\%, three seeds) despite near-identical validation loss "
    "($|\\Delta|=0.012$)---an ``equally-good-but-different'' outcome that aggregate metrics "
    "hide. In single-seed probes, lower precision brought divergence onset earlier (fp16 by "
    "$\\le$ step 50, bf16 by step 400). Our pre-registered persistence hypothesis was refuted "
    "at 10M; the resulting scale-dependence is reported as a post-hoc, hypothesis-generating "
    "observation, not a confirmed law. The single divergent point confounds backend with "
    "machine and build, so we attribute it to a cross-system difference rather than the "
    "numerical path alone. Small-model, many-run studies on open corpora make this failure "
    "mode measurable and reproducible."
)

# (file, section title, drop-leading-note?)
SECTIONS = [
    ("introduction_draft.md", "Introduction", False),
    ("methods_draft.md", "Methods", False),
    ("results_draft.md", "Results", False),
    ("discussion_draft.md", "Discussion", False),
    ("related_work_draft.md", "Related work and positioning", True),
]


def convert_cites(text):
    def repl(m):
        inner = m.group(1)
        keys = [k.strip() for k in re.split(r"[;,]", inner)]
        if keys and all(k in BIB_KEYS for k in keys):
            return r"\citep{" + ",".join(keys) + "}"
        return m.group(0)
    return re.sub(r"\[([^\]\n]+)\]", repl, text)


def strip_header_and_note(md, drop_note):
    lines = md.splitlines()
    out, started = [], False
    for ln in lines:
        if not started:
            if ln.startswith("# "):          # drop the h1 title
                continue
            if drop_note and (ln.strip().startswith("(") or ln.strip() == ""):
                if ln.strip().endswith(")"):  # single-line note
                    continue
                # multi-line parenthetical: skip until a line ending ')'
                continue
            if ln.strip():
                started = True
        out.append(ln)
    return "\n".join(out)


_UNI = {
    "↔": r"$\leftrightarrow$", "≤": r"$\le$", "≥": r"$\ge$",
    "±": r"$\pm$", "→": r"$\rightarrow$", "×": r"$\times$",
    "≈": r"$\approx$", "≫": r"$\gg$", "Δ": r"$\Delta$",
    "α": r"$\alpha$", "—": "---", "–": "--",
    "✓": r"\checkmark{}", "✗": r"($\times$)", "≥": r"$\ge$",
}


def sanitize_unicode(tex):
    for u, r in _UNI.items():
        tex = tex.replace(u, r)
    return tex


def pandoc(md):
    p = subprocess.run(["pandoc", "-f", "markdown", "-t", "latex", "--wrap=preserve"],
                       input=md, capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit("pandoc failed: " + p.stderr)
    return sanitize_unicode(p.stdout)


def main():
    body = []
    for fname, title, drop_note in SECTIONS:
        md = open(os.path.join(MS, fname)).read()
        md = strip_header_and_note(md, drop_note)
        md = convert_cites(md)
        body.append(f"\\section{{{title}}}\n" + pandoc(md))

    figures = r"""

\begin{figure}[t]\centering
\includegraphics[width=0.86\textwidth]{fig_abstract_schematic.png}
\caption{Graphical abstract. One training recipe (same seed, data, code) on CPU/CUDA/MPS
yields a near-identical model at 10M (0.2\% prediction disagreement) but divergent
``equally-good-but-different'' models at 50M (13.2\%, equal loss).}
\label{fig:abstract}\end{figure}

\begin{figure}[t]\centering
\includegraphics[width=0.98\textwidth]{fig_h1_scale_emergence.png}
\caption{Cross-system prediction disagreement. \emph{Left:} vs.\ training step (seed 0) for
10M CUDA$\leftrightarrow$CPU and 50M CUDA$\leftrightarrow$MPS. \emph{Right:} final-step
disagreement by size; bars are the mean over seeds $\{0,1,2\}$, error bars $\pm1$ SD; dashed
line marks the pre-registered 10\% band.}
\label{fig:h1}\end{figure}

\begin{figure}[t]\centering
\includegraphics[width=0.7\textwidth]{fig_h3_precision.png}
\caption{Precision and divergence onset at 50M on CUDA (single seed): fp32$\leftrightarrow$bf16
and fp32$\leftrightarrow$fp16, with fp32 CUDA$\leftrightarrow$MPS for reference. Onset
$\le$ step 50 (fp16) and step 400 (bf16).}
\label{fig:h3}\end{figure}
"""

    backmatter = r"""
\section*{Data and code availability}
All code, the sealed pre-registration, the analysis, and the figures are available at
\texttt{https://github.com/tckamijo/repro-pretrain} (archived at Zenodo, DOI to be added). The
corpus is not redistributed as raw text; it is exactly reconstructible from the PMC Open Access
subset using the included collector and verifiable against the recorded SHA-256
(\texttt{9d6b168e...5b0a27}, 300{,}120{,}401 bytes). Per-run outputs (validation loss, held-out
predictions, weight fingerprints, PyTorch build) are provided for all 27 runs, and each figure
ships with a provenance sidecar. A claim-to-source verification worksheet is included.

\section*{Competing interests}
The author declares no competing interests.

\section*{Statement on the use of AI tools}
In preparing this work the author used a large language model (Anthropic's Claude) as an
assistive tool: drafting and editing the manuscript; writing and scaffolding the
data-collection, training-harness, analysis, and figure-generation code; assisting with the
literature search; and running an internal adversarial review. All experiments were executed by
the author on the author's own hardware, and every reported quantitative result was produced by
the analysis code and independently verified by the author against the raw per-run outputs. The
author designed the study, sealed the pre-registration, checked all numbers, claims, and
citations, and takes full responsibility for the content and its scientific validity. No data,
results, or citations were fabricated.
"""

    main_tex = (
        "\\documentclass{article}\n"
        f"\\usepackage{PKG_OPT}{{tmlr}}\n"
        "\\usepackage{graphicx}\n\\usepackage{booktabs}\n\\usepackage{amsmath}\n"
        "\\usepackage{amssymb}\n\\usepackage{longtable}\n\\usepackage{array}\n"
        "\\usepackage{calc}\n\\providecommand{\\real}[1]{#1}\n"  # pandoc width-computed tables
        "\\usepackage[T1]{fontenc}\n\\usepackage{microtype}\n"
        f"\\title{{{TITLE}}}\n"
        f"\\author{{{AUTHOR}}}\n"
        "\\def\\month{07}\\def\\year{2026}\n"
        "\\begin{document}\n\\maketitle\n"
        f"\\begin{{abstract}}\n{ABSTRACT}\n\\end{{abstract}}\n\n"
        + "\n\n".join(body)
        + "\n" + figures
        + "\n" + backmatter +
        "\n\\bibliographystyle{tmlr}\n\\bibliography{refs}\n"
        "\\end{document}\n"
    )
    tex_name = f"{OUT_PDF}.tex"
    open(os.path.join(HERE, tex_name), "w").write(main_tex)
    # ensure bib + figures are locatable next to main.tex
    subprocess.run(["cp", BIB, os.path.join(HERE, "refs.bib")])
    for fig in ("fig_abstract_schematic.png", "fig_h1_scale_emergence.png", "fig_h3_precision.png"):
        subprocess.run(["cp", os.path.join(MS, "..", "analysis", fig), HERE])
    print(f"[build] {tex_name} written (anon={ANON}); running tectonic…")
    r = subprocess.run(["tectonic", tex_name, "--keep-logs", "--print"],
                       cwd=HERE, capture_output=True, text=True)
    sys.stdout.write(r.stdout[-2000:]); sys.stderr.write(r.stderr[-3000:])
    if r.returncode == 0 and os.path.exists(os.path.join(HERE, f"{OUT_PDF}.pdf")):
        sz = os.path.getsize(os.path.join(HERE, f"{OUT_PDF}.pdf"))
        print(f"\n[build] OK -> {OUT_PDF}.pdf ({sz//1024} KB)")
    else:
        print(f"\n[build] tectonic rc={r.returncode}")


if __name__ == "__main__":
    main()
