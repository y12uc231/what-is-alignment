"""Every arXiv id or corpus id linked from the repo's markdown must be in data/papers.jsonl.
Usage: python -I check_cites.py [files...]  (default: README.md OPEN_PROBLEMS.md docs/*.md)"""
import json, re, sys
from pathlib import Path
ROOT = Path.cwd()
ids = {json.loads(l)["id"] for l in (ROOT / "data/papers.jsonl").read_text().splitlines() if l.strip()}
files = [Path(a) for a in sys.argv[1:]] or [p for p in [ROOT / "README.md", ROOT / "OPEN_PROBLEMS.md", *sorted((ROOT / "docs").glob("*.md"))] if p.exists()]
bad = 0
for f in files:
    for m in set(re.findall(r"arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d{4,5})", f.read_text())):
        if m not in ids:
            print(f"FAIL {f.name}: {m} not in corpus"); bad += 1
print(f"cite check: {bad} problems in {len(files)} files")
sys.exit(1 if bad else 0)
