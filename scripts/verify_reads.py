"""Check that deep reads quote the paper verbatim and cover it from start to end.

Each reading is reads/<id>.json:
  {"id": ..., "title": ..., "text_path": "fulltext/<id>.txt",
   "quotes": [{"section": "method|results|limitations|...", "quote": "..."}],
   "key_numbers": [{"claim": "...", "quote": "..."}], ...}

A read passes when every quote is found in the text, the quotes cover the method, results and
limitations/discussion parts, and at least one quote sits in the last 40% of the body
(the body ends at the references heading).

Section labels are self-reported, so the checker also finds each quote's real heading in the text
and requires quotes from at least 3 distinct real sections.

Usage: python3 -I scripts/verify_reads.py [--show] [reads/*.json]
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path.cwd()
REQUIRED = {"method", "results", "limitations"}
LATE = 0.6

SUBS = {"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-",
        "−": "-", "ﬁ": "fi", "ﬂ": "fl", "­": ""}


def norm(s):
    s = unicodedata.normalize("NFKC", s)
    for a, b in SUBS.items():
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip().lower()


def body_end(text):
    # Use the first references heading after the opening 30% of the text (some extractions repeat the
    # reference list before the body); fall back to the last one, then to the whole text.
    ms = list(re.finditer(r"\n## *(?:\d+\s*)?(references|bibliography)\b", text, re.I))
    later = [m for m in ms if m.start() > 0.3 * len(text)]
    if later:
        return later[0].start()
    return ms[-1].start() if ms else len(text)


def section_kind(label):
    label = label.lower()
    if any(k in label for k in ("limit", "discussion", "conclusion", "future", "threat", "broader")):
        return "limitations"
    if any(k in label for k in ("result", "experiment", "evaluation", "finding", "analysis", "ablation")):
        return "results"
    if any(k in label for k in ("method", "environment", "design", "benchmark", "setup", "approach", "framework", "task", "threat model", "construction", "overview", "emulat")):
        return "method"
    return label


def sections(raw):
    """Split text at '## ' headings; return (normalised joined text, [(start, heading)])."""
    parts = re.split(r"\n(?=## )", raw)
    text, marks = "", []
    for part in parts:
        head = part.splitlines()[0].lstrip("# ").strip() if part.startswith("## ") else "(front matter)"
        marks.append((len(text), head))
        text += norm(part) + " "
    return text, marks


def heading_at(marks, pos):
    head = marks[0][1]
    for start, h in marks:
        if start > pos:
            break
        head = h
    return head


def check(path, show=False):
    r = json.loads(path.read_text())
    text_path = ROOT / r["text_path"]
    if not text_path.exists():
        return r["id"], False, [f"missing text {r['text_path']}"]
    raw = text_path.read_text(encoding="utf-8", errors="replace")
    end = body_end(raw)
    body, marks = sections(raw[:end])
    whole = norm(raw)
    problems, kinds, true_heads, spots = [], set(), set(), []
    for q in r.get("quotes", []):
        nq = norm(q["quote"])
        pos = body.find(nq)
        if pos < 0:
            # Appendix quotes count as found but not as body coverage.
            if nq in whole:
                kinds.add(section_kind(q.get("section", "")))
                true_heads.add("(appendix)")
                spots.append((None, "(appendix)", q.get("section", "")))
                continue
            problems.append(f"not found: {q['quote'][:80]!r}")
            continue
        kinds.add(section_kind(q.get("section", "")))
        head = heading_at(marks, pos)
        true_heads.add(head)
        spots.append((pos / max(1, len(body)), head, q.get("section", "")))
    for k in r.get("key_numbers", []):
        if k.get("quote") and norm(k["quote"]) not in whole:
            problems.append(f"key number quote not found: {k['quote'][:80]!r}")
    missing = REQUIRED - kinds
    if missing:
        problems.append(f"no quote labelled: {', '.join(sorted(missing))}")
    # Label-independent checks: where the quotes really sit in the paper.
    found = [x for x, _, _ in spots if x is not None]
    if not found or max(found) < LATE:
        problems.append(f"latest body quote at {max(found, default=0):.0%} of the paper")
    if len(marks) >= 5 and len(true_heads) < 3:
        problems.append(f"quotes come from only {len(true_heads)} distinct sections")
    # Texts without headings (some PDF extractions): require spread by position instead.
    if len(marks) < 5 and (not found or min(found) > 0.4 or len(found) < 5):
        problems.append("text has no section headings and quotes are not spread across it")
    if show:
        for x, head, label in sorted(spots, key=lambda t: (t[0] is None, t[0] or 0)):
            where = "appx" if x is None else f"{x:4.0%}"
            print(f"    {where}  {head[:60]:60}  label: {label[:40]}")
    return r["id"], not problems, problems


def main():
    args = sys.argv[1:]
    show = "--show" in args
    args = [a for a in args if a != "--show"]
    paths = [Path(p) for p in args] or sorted((ROOT / "reads").glob("*.json"))
    ok = 0
    for p in paths:
        pid, passed, problems = check(p, show)
        ok += passed
        print(f"{'PASS' if passed else 'FAIL'} {pid}" + ("" if passed else "  " + "; ".join(problems)))
    print(f"\n{ok}/{len(paths)} reads pass")
    return 0 if ok == len(paths) else 1


if __name__ == "__main__":
    sys.exit(main())
