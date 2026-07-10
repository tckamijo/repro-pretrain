#!/usr/bin/env python3
"""corpus/collect_neuro.py — neural/biomedical OA corpus collector for repro-pretrain Step 2.

Source : NCBI PMC Open Access subset via E-utilities (esearch + efetch JATS XML).
         PMC/API is anti-bot-friendly (lit-fetch 教訓: publisher 直叩きは全滅、PMC は素直).
License: per-article gate on the JATS <license> href. KEEP only permissive
         (CC0 / CC-BY / CC-BY-SA). REJECT anything with NC or ND. Rejections are
         logged to rejected.jsonl for provenance transparency. The esearch
         "open access[filter]" alone still admits NC/ND, so this gate is mandatory.
Output : byte-level corpus. Per-doc cleaned UTF-8 text -> data/docs/<PMCID>.txt,
         provenance -> data/manifest.jsonl. Deterministic assembly (--assemble)
         sorts docs by PMCID and concatenates into data/neuro.bin (uint8 memmap
         that harness/train_scale.py --corpus consumes).

Politeness: <=3 req/s without API key (sleep 0.35s), retry w/ backoff on 429/5xx.
Stdlib only (grant-feed sources/_base.py 流儀), no third-party deps.

Usage
  # collect (resumable; safe to re-run / Ctrl-C):
  python corpus/collect_neuro.py --query neuroscience --target-mb 300
  python corpus/collect_neuro.py --query neuroscience --max-fetch 40 --smoke
  # assemble neuro.bin from collected docs (deterministic):
  python corpus/collect_neuro.py --assemble
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
USER_AGENT = "repro-pretrain-corpus-bot/0.1 (Mac mini, contact: chuyo.km@gmail.com)"
TIMEOUT = 30
SLEEP = 0.35  # <=3 req/s without API key
DOC_SEP = b"\n\n<|endoftext|>\n\n"  # document boundary in neuro.bin
MIN_CHARS = 2000  # drop stubs / metadata-only records

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
DOCS = os.path.join(DATA, "docs")
MANIFEST = os.path.join(DATA, "manifest.jsonl")
REJECTED = os.path.join(DATA, "rejected.jsonl")
BIN = os.path.join(DATA, "neuro.bin")


# --------------------------------------------------------------------------- HTTP
def http_get(url: str, tries: int = 4) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    delay = 1.0
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < tries - 1:
                time.sleep(delay); delay *= 2; continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < tries - 1:
                time.sleep(delay); delay *= 2; continue
            raise
    raise RuntimeError("unreachable")


def esearch(query: str, retstart: int, retmax: int) -> tuple[int, list[str]]:
    term = f"{query} AND open access[filter]"
    url = (f"{EUTILS}/esearch.fcgi?db=pmc&term={urllib.parse.quote(term)}"
           f"&retstart={retstart}&retmax={retmax}&retmode=json")
    d = json.loads(http_get(url).decode("utf-8", "replace"))["esearchresult"]
    return int(d["count"]), d.get("idlist", [])


def efetch_jats(pmcid: str) -> str:
    url = f"{EUTILS}/efetch.fcgi?db=pmc&id={pmcid}&retmode=xml"
    return http_get(url).decode("utf-8", "replace")


# --------------------------------------------------------------- license gate
# Accept: CC0/public-domain, CC-BY, CC-BY-SA.  Reject: any NC or ND.
_CC_RE = re.compile(r"creativecommons\.org/(licenses|publicdomain)/([a-z0-9-]+)", re.I)


def classify_license(xml: str) -> tuple[str, str | None]:
    """Return (verdict, license_id). verdict in {permissive, restricted, unknown}."""
    # Normalize line-wrap artifacts (JATS wraps long hrefs: 'by-\nnc-nd' -> 'by-nc-nd')
    flat = re.sub(r"\s+", "", xml)
    best = None
    for m in _CC_RE.finditer(flat):
        kind, code = m.group(1).lower(), m.group(2).lower()
        if kind == "publicdomain":  # zero/1.0, mark/1.0
            return "permissive", "cc0"
        best = code
        if "nc" in code or "nd" in code:
            return "restricted", code
        if code in ("by", "by-sa"):
            return "permissive", code
    if best:
        return "unknown", best
    # No CC href — check for explicit CC0 / public-domain wording
    low = flat.lower()
    if "publicdomain" in low or "cc0" in low:
        return "permissive", "cc0"
    return "unknown", None


# --------------------------------------------------------------- text extract
def _first(pattern: str, xml: str) -> str:
    m = re.search(pattern, xml, re.S)
    return strip_tags(m.group(1)) if m else ""


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s)
    return html.unescape(s)


def extract_body_text(xml: str) -> str:
    m = re.search(r"<body\b[^>]*>(.*?)</body>", xml, re.S)
    if not m:
        return ""
    body = m.group(1)
    # Drop non-prose blocks that hurt a byte-level LM (tables, figures, refs, math, formulas)
    for tag in ("table-wrap", "fig", "ref-list", "disp-formula", "inline-formula",
                "tex-math", "mml:math", "table", "supplementary-material"):
        body = re.sub(rf"<{tag}\b.*?</{tag}>", " ", body, flags=re.S)
    # Prefer paragraph & section-title text so we keep prose, drop stray markup
    chunks = re.findall(r"<(?:p|title)\b[^>]*>(.*?)</(?:p|title)>", body, re.S)
    text = "\n\n".join(strip_tags(c) for c in chunks) if chunks else strip_tags(body)
    # Whitespace normalize (keep paragraph breaks)
    text = re.sub(r"[ \t ]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ------------------------------------------------------------------- state I/O
def load_seen() -> set[str]:
    seen: set[str] = set()
    for path in (MANIFEST, REJECTED):
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                for line in f:
                    try:
                        seen.add(json.loads(line)["pmcid"])
                    except Exception:
                        pass
    return seen


def append_jsonl(path: str, rec: dict) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def current_corpus_bytes() -> int:
    if not os.path.exists(MANIFEST):
        return 0
    total = 0
    with open(MANIFEST, encoding="utf-8") as f:
        for line in f:
            try:
                total += json.loads(line)["bytes"]
            except Exception:
                pass
    return total


# ---------------------------------------------------------------- collect loop
def collect(query: str, target_mb: float | None, max_fetch: int | None) -> None:
    os.makedirs(DOCS, exist_ok=True)
    seen = load_seen()
    target_bytes = int(target_mb * 1_000_000) if target_mb else None
    have = current_corpus_bytes()
    kept = fetched = rejected = 0
    print(f"[start] seen={len(seen)} existing_corpus={have/1e6:.1f}MB "
          f"target={'%.0fMB' % target_mb if target_mb else 'n/a'} max_fetch={max_fetch}")

    retstart, page = 0, 200
    total_hits = None
    while True:
        if target_bytes and have >= target_bytes:
            print(f"[done] target reached: {have/1e6:.1f}MB"); break
        if max_fetch and fetched >= max_fetch:
            print(f"[done] max_fetch reached: {fetched}"); break
        total_hits, ids = esearch(query, retstart, page)
        time.sleep(SLEEP)
        if not ids:
            print(f"[done] esearch exhausted at retstart={retstart}"); break
        retstart += page
        for pmcid in ids:
            if pmcid in seen:
                continue
            if max_fetch and fetched >= max_fetch:
                break
            if target_bytes and have >= target_bytes:
                break
            seen.add(pmcid)
            try:
                xml = efetch_jats(pmcid)
            except Exception as e:
                append_jsonl(REJECTED, {"pmcid": pmcid, "reason": f"fetch_error:{e}"})
                time.sleep(SLEEP); continue
            fetched += 1
            time.sleep(SLEEP)

            verdict, lic = classify_license(xml)
            if verdict != "permissive":
                append_jsonl(REJECTED, {"pmcid": pmcid, "reason": f"license_{verdict}",
                                        "license": lic})
                rejected += 1
                continue
            text = extract_body_text(xml)
            if len(text) < MIN_CHARS:
                append_jsonl(REJECTED, {"pmcid": pmcid, "reason": "too_short",
                                        "chars": len(text), "license": lic})
                rejected += 1
                continue
            title = _first(r"<article-title[^>]*>(.*?)</article-title>", xml)[:300]
            data = text.encode("utf-8")
            with open(os.path.join(DOCS, f"{pmcid}.txt"), "w", encoding="utf-8") as f:
                f.write(text)
            append_jsonl(MANIFEST, {
                "pmcid": pmcid, "title": title.strip(), "license": lic,
                "chars": len(text), "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "fetched": date.today().isoformat(),
                "source": "PMC-OA/efetch",
            })
            kept += 1
            have += len(data)
            if kept % 25 == 0:
                print(f"  kept={kept} rejected={rejected} fetched={fetched} "
                      f"corpus={have/1e6:.1f}MB (hits={total_hits})")
    print(f"[summary] kept={kept} rejected={rejected} fetched={fetched} "
          f"corpus={have/1e6:.1f}MB")


# ---------------------------------------------------------------- assemble bin
def assemble() -> None:
    if not os.path.exists(MANIFEST):
        sys.exit("no manifest — run collect first")
    pmcids = []
    with open(MANIFEST, encoding="utf-8") as f:
        for line in f:
            try:
                pmcids.append(json.loads(line)["pmcid"])
            except Exception:
                pass
    pmcids = sorted(set(pmcids), key=lambda x: int(x))  # deterministic order
    h = hashlib.sha256()
    total = 0
    with open(BIN, "wb") as out:
        for i, pmcid in enumerate(pmcids):
            p = os.path.join(DOCS, f"{pmcid}.txt")
            if not os.path.exists(p):
                continue
            with open(p, "rb") as f:
                data = f.read()
            if i:
                out.write(DOC_SEP); h.update(DOC_SEP); total += len(DOC_SEP)
            out.write(data); h.update(data); total += len(data)
    print(f"[assemble] docs={len(pmcids)} neuro.bin={total/1e6:.2f}MB "
          f"sha256={h.hexdigest()}")
    print(f"[assemble] path={BIN}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", default="neuroscience",
                    help="PMC search term (open-access filter is added automatically)")
    ap.add_argument("--target-mb", type=float, default=None)
    ap.add_argument("--max-fetch", type=int, default=None)
    ap.add_argument("--smoke", action="store_true", help="alias for a tiny bounded run")
    ap.add_argument("--assemble", action="store_true",
                    help="build neuro.bin from collected docs (deterministic) and exit")
    a = ap.parse_args()
    if a.assemble:
        assemble(); return
    if a.smoke and a.max_fetch is None:
        a.max_fetch = 40
    if a.target_mb is None and a.max_fetch is None:
        sys.exit("specify --target-mb or --max-fetch (or --smoke)")
    collect(a.query, a.target_mb, a.max_fetch)


if __name__ == "__main__":
    main()
