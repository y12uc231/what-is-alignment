"""Every quotation in the prose must occur verbatim in a full text we hold.

Scans README.md and docs/*.md for text in double quotes ("..." or “...”) of at least MIN_WORDS words and checks
that it occurs (after normalisation) in at least one fulltext/*.txt. Shorter quoted phrases are treated as terms.
A quotation may end with an ellipsis "..." to mark a cut; each part between ellipses is checked separately.

Usage: python -I scripts/check_doc_quotes.py [--verbose] [files...]
"""
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path.cwd()
MIN_WORDS = 5
SUBS = {"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-",
        "−": "-", "ﬁ": "fi", "ﬂ": "fl", "­": "", "…": "..."}


def norm(s):
    s = unicodedata.normalize("NFKC", s)
    for a, b in SUBS.items():
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip().lower()


def main():
    args = sys.argv[1:]
    verbose = "--verbose" in args
    args = [a for a in args if a != "--verbose"]
    files = [Path(a) for a in args] or [p for p in [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
                                         if p.exists()]
    corpus = [norm(p.read_text(encoding="utf-8", errors="replace")) for p in sorted((ROOT / "fulltext").glob("*.txt"))]
    bad = total = 0
    for f in files:
        text = f.read_text()
        # Skip fenced code blocks.
        text = re.sub(r"```.*?```", "", text, flags=re.S)
        quotes = []
        for para in re.split(r"\n\s*\n", text):
            # Pair straight double quotes in order within a paragraph (1st with 2nd, 3rd with 4th, ...).
            pos = [i for i, ch in enumerate(para) if ch == '"']
            quotes += [para[a + 1:b] for a, b in zip(pos[0::2], pos[1::2])]
            quotes += re.findall(r"“([^”]+)”", para)
        for q in quotes:
            if len(q.split()) < MIN_WORDS:
                continue
            parts = [p.strip(" .,;:") for p in re.split(r"\.\.\.|…|\[\.\.\.\]", q) if len(p.split()) >= 3]
            total += 1
            missing = [p for p in parts if not any(norm(p) in c for c in corpus)]
            if missing:
                bad += 1
                print(f"FAIL {f.name}: {q[:100]!r}")
            elif verbose:
                print(f"ok   {f.name}: {q[:80]!r}")
    print(f"\nquote check: {total - bad}/{total} quotations found in full texts")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
