"""Check definition cards (data/definitions/*.yaml) and case cards (data/cases/*.yaml).

Every quote must occur verbatim (after whitespace/quote-mark normalisation) in fulltext/<source>.txt,
every source must be in the corpus (data/papers.jsonl plus data/corpus/*.jsonl), and enumerated fields
must use the allowed values.

Usage: python -I scripts/verify_cards.py [--quiet] [files...]
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

import yaml

ROOT = Path.cwd()
SUBS = {"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-",
        "−": "-", "ﬁ": "fi", "ﬂ": "fl", "­": "", "…": "..."}

CASE_VERDICTS = {"alignment", "not-alignment", "boundary"}
SETTINGS = {"deployed", "lab-elicited", "instructed", "model-organism", "simulated-agentic", "training-run", "toy-environment"}
YNU = {"yes", "no", "partly", "unknown"}
SOURCES_OF_DIVERGENCE = {"specification", "generalization", "inserted", "imitation", "instruction-from-principal",
                         "capability-limit", "adversarial-input", "unclear"}
DEF_TARGETS = {"intentions", "instructions", "preferences", "values", "interests", "specification", "human-approval",
               "norms", "goals", "not-stated", "other"}
DEF_PRINCIPALS = {"operator", "user", "developer", "humanity", "multiple", "unspecified"}
DEF_BM = {"behavior", "motivation", "both", "unclear"}


def norm(s):
    s = unicodedata.normalize("NFKC", s)
    for a, b in SUBS.items():
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip().lower()


def corpus_ids():
    ids = set()
    files = [ROOT / "data/papers.jsonl", *sorted((ROOT / "data/corpus").glob("*.jsonl"))]
    for f in files:
        if f.exists():
            for line in f.read_text().splitlines():
                if line.strip():
                    ids.add(json.loads(line)["id"])
    return ids


_texts = {}


def text_of(src):
    if src not in _texts:
        p = ROOT / "fulltext" / f"{src}.txt"
        _texts[src] = norm(p.read_text(encoding="utf-8", errors="replace")) if p.exists() else None
    return _texts[src]


def check_quote(src, quote, where, problems):
    t = text_of(src)
    if t is None:
        problems.append(f"{where}: no fulltext/{src}.txt")
    elif norm(quote) not in t:
        problems.append(f"{where}: quote not found in {src}: {quote[:70]!r}")


def check_def(c, ids, problems):
    w = c.get("id", "?")
    for k in ("id", "source", "year", "term", "definition_quote", "target", "principal", "behavior_or_motivation"):
        if k not in c:
            problems.append(f"{w}: missing {k}")
    src = c.get("source")
    if src not in ids:
        problems.append(f"{w}: source {src} not in corpus")
    if c.get("target") not in DEF_TARGETS:
        problems.append(f"{w}: bad target {c.get('target')}")
    if c.get("principal") not in DEF_PRINCIPALS:
        problems.append(f"{w}: bad principal {c.get('principal')}")
    if c.get("behavior_or_motivation") not in DEF_BM:
        problems.append(f"{w}: bad behavior_or_motivation {c.get('behavior_or_motivation')}")
    if src and c.get("definition_quote"):
        check_quote(src, c["definition_quote"], f"{w}.definition_quote", problems)
    for field in ("includes", "excludes"):
        for i, item in enumerate(c.get(field) or []):
            check_quote(item.get("source", src), item.get("quote", ""), f"{w}.{field}[{i}]", problems)


def check_case(c, ids, problems):
    w = c.get("id", "?")
    for k in ("id", "title", "year", "sources", "system", "setting", "what_happened", "quotes", "authors_term",
              "evidence", "candidate_verdict", "reasoning"):
        if k not in c:
            problems.append(f"{w}: missing {k}")
    for s in c.get("sources", []):
        if s not in ids:
            problems.append(f"{w}: source {s} not in corpus")
    if c.get("setting") not in SETTINGS:
        problems.append(f"{w}: bad setting {c.get('setting')}")
    if c.get("candidate_verdict") not in CASE_VERDICTS:
        problems.append(f"{w}: bad verdict {c.get('candidate_verdict')}")
    ev = c.get("evidence") or {}
    for k in ("knew", "could"):
        if (ev.get(k) or {}).get("answer") not in YNU:
            problems.append(f"{w}: evidence.{k}.answer must be one of {sorted(YNU)}")
    if ev.get("source_of_divergence") not in SOURCES_OF_DIVERGENCE:
        problems.append(f"{w}: bad source_of_divergence {ev.get('source_of_divergence')}")
    if not c.get("quotes"):
        problems.append(f"{w}: no quotes")
    for i, q in enumerate(c.get("quotes") or []):
        src = q.get("source") or (c.get("sources") or [None])[0]
        check_quote(src, q.get("quote", ""), f"{w}.quotes[{i}]", problems)
    if not str(c.get("reasoning", "")).startswith("Our reading"):
        problems.append(f"{w}: reasoning must start with 'Our reading'")


def main():
    args = sys.argv[1:]
    quiet = "--quiet" in args
    args = [a for a in args if a != "--quiet"]
    ids = corpus_ids()
    files = [Path(a) for a in args] or [*sorted((ROOT / "data/definitions").glob("*.yaml")),
                                         *sorted((ROOT / "data/cases").glob("*.yaml"))]
    total, bad, seen = 0, 0, set()
    for f in files:
        cards = yaml.safe_load(f.read_text()) or []
        kind = "def" if "definitions" in f.parts else "case"
        for c in cards:
            total += 1
            problems = []
            if c.get("id") in seen:
                problems.append(f"{c.get('id')}: duplicate id")
            seen.add(c.get("id"))
            (check_def if kind == "def" else check_case)(c, ids, problems)
            if problems:
                bad += 1
                for p in problems:
                    print(f"FAIL {f.name}: {p}")
            elif not quiet:
                print(f"PASS {c.get('id')}")
    print(f"\n{total - bad}/{total} cards pass")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
