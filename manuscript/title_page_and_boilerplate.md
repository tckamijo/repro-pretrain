# Title page and boilerplate

## Title
Cross-hardware reproducibility of language-model pretraining breaks down with model scale:
a zero-cost heterogeneous-fleet study

## Author
Tadanobu C. Kamijo¹*

¹ Department of Systems Physiology, Graduate School of Medicine, University of the Ryukyus,
Okinawa, Japan.

\* Corresponding author. E-mail: (institutional address — user to fill).

（共著者は user 確定。現状 single-author draft。）

## Competing Interests
The author declares no competing interests.

## Funding
（KAKENHI 番号は user 確認。該当あれば記載、なければ "This work received no specific grant." ）

## Author Contributions (CRediT)
T.C.K.: conceptualization, methodology, software, formal analysis, investigation, data
curation, writing – original draft, writing – review & editing, visualization.

## Data and Code Availability

All code, the sealed pre-registration, the analysis, and the figures are available at
`https://github.com/tckamijo/repro-pretrain` (to be made public on acceptance). The corpus
is not redistributed as raw text; it is **exactly reconstructible** from the open PMC Open
Access subset using the included collector (`corpus/collect_neuro.py`), and its integrity is
verifiable against the recorded SHA-256
(`9d6b168e700a2a7b4bd2bbc609449ff6e74952819a0453c3ac0b82d93a5b0a27`, 300,120,401 bytes). The
per-run outputs (validation loss, held-out predictions, weight fingerprints, and PyTorch
version) are provided for all 27 runs. Each figure ships with an `artifact-provenance` sidecar
recording its generating commit, environment, and description.

## Pre-registration statement
Hypotheses, decision thresholds, feasibility caveats, and an anti-rescue ledger were sealed
prior to the full experiment (repository commit 585abe1; document SHA-256 bb177f06…). No
threshold or hypothesis was modified after unsealing; the one refuted hypothesis (H1) is
reported as refuted.

## Ethical standards
This study did not involve human participants, animals, or personal data. The corpus derives
solely from openly licensed (CC0/CC-BY/CC-BY-SA) published open-access literature.
