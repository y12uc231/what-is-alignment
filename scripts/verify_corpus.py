"""Check data/papers.jsonl against arXiv metadata; --fix fills title/authors/date from arXiv.

Each row: {"id", "kind": "arxiv"|"web", "url", "title", "authors", "date", "venue", "cluster", "note", "note_basis"}
arXiv rows must match the arXiv title (case/space-insensitive, >=0.9 similarity). Metadata is cached in
data/arxiv_meta.jsonl. Web rows need a url. Duplicated ids fail.
Usage: python -I verify_corpus.py [--fix]
"""
import difflib, json, re, subprocess, sys
from pathlib import Path

ROOT = Path.cwd(); KIT = Path(__file__).resolve().parent
P = ROOT / "data/papers.jsonl"; C = ROOT / "data/arxiv_meta.jsonl"
fix = "--fix" in sys.argv
rows = [json.loads(l) for l in P.read_text().splitlines() if l.strip()]
cache = {}
if C.exists():
    for l in C.read_text().splitlines():
        if l.strip():
            m = json.loads(l); cache[m["id"]] = m
need = [r["id"] for r in rows if r.get("kind", "arxiv") == "arxiv" and r["id"] not in cache]
for i in range(0, len(need), 25):
    out = subprocess.run([sys.executable, "-I", str(KIT / "arxiv_meta.py"), *need[i:i + 25]], capture_output=True, text=True).stdout
    with C.open("a") as f:
        for l in out.splitlines():
            m = json.loads(l)
            if m.get("ok"):
                cache[m["id"]] = m; f.write(json.dumps(m) + "\n")
    print(f"fetched {min(i + 25, len(need))}/{len(need)}", file=sys.stderr)
norm = lambda s: re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()
bad, seen = [], set()
for r in rows:
    if r["id"] in seen:
        bad.append(f"duplicate {r['id']}")
    seen.add(r["id"])
    if r.get("kind", "arxiv") == "web":
        if not r.get("url"):
            bad.append(f"{r['id']}: web row without url")
        continue
    m = cache.get(r["id"])
    if not m:
        bad.append(f"{r['id']}: no arXiv metadata (wrong id?)"); continue
    if fix:
        r.update(title=m["title"], authors=m["authors"], date=m["date"])
        # Venue only from an explicit acceptance of a main-track paper; workshops, submissions and
        # "under review" comments are skipped (an earlier version mislabelled workshop papers).
        c = m.get("comment") or ""
        if c and not r.get("venue") and re.search(r"accepted|to appear|published|camera.ready", c, re.I) \
                and not re.search(r"workshop|submitted|under review|in submission|preprint|\w+\s*@\s*(ICLR|ICML|NeurIPS|ACL|EMNLP|NAACL|COLM)", c, re.I):
            v = re.search(r"\b(ICLR|ICML|NeurIPS|EACL|ACL|EMNLP|NAACL|COLM|AAAI|TMLR|CVPR|USENIX Security|IEEE S&P|CCS)[ ']*(20\d\d)", c)
            if v: r["venue"] = v.group(0).strip() + (" (Findings)" if re.search(r"findings", c, re.I) else "")
    sim = difflib.SequenceMatcher(None, norm(r.get("title")), norm(m["title"])).ratio()
    if sim < 0.9:
        bad.append(f"{r['id']}: title mismatch ({sim:.2f}) ours={r.get('title')!r} arXiv={m['title']!r}")
if fix:
    P.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
for b in bad:
    print("FAIL", b)
print(f"{len(rows) - len(bad)}/{len(rows)} corpus rows pass")
sys.exit(1 if bad else 0)
