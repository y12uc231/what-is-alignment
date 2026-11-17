"""Fetch full text for arXiv ids into fulltext/<id>.txt (HTML via html2txt; PDF fallback via pypdf).

Usage: .venv/bin/python -I scripts/fetch_text.py ID [ID ...]
Skips ids whose text already exists (>3000 chars). Prints id, source, words.
"""
import io, re, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path.cwd()
FT = ROOT / "fulltext"; HTML = FT / "html"; HTML.mkdir(parents=True, exist_ok=True)

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "survey-reader/0.1 (research)"})
    return urllib.request.urlopen(req, timeout=60).read()

def from_pdf(data):
    from pypdf import PdfReader
    r = PdfReader(io.BytesIO(data)); parts = []
    for i, p in enumerate(r.pages):
        t = p.extract_text() or ""
        # PDF text has no '## ' headings; promote likely section headings so verify_reads can locate quotes.
        t = re.sub(r"(?m)^(\d{1,2}(?:\.\d{1,2})?\s+[A-Z][A-Za-z ,:&\-]{2,60})$", r"\n## \1", t)
        t = re.sub(r"(?m)^(References|REFERENCES|Bibliography|Acknowledg(?:e)?ments?|Abstract|ABSTRACT|Limitations|Conclusions?)\s*$", r"\n## \1", t)
        parts.append(t)
    return "\n".join(parts)

for aid in sys.argv[1:]:
    out = FT / f"{aid}.txt"
    if out.exists() and out.stat().st_size > 3000:
        print(aid, "cached", len(out.read_text(errors="replace").split())); continue
    src = "html"
    try:
        hp = HTML / f"{aid}.html"
        if not (hp.exists() and hp.stat().st_size > 5000):
            hp.write_bytes(get(f"https://arxiv.org/html/{aid}")); time.sleep(1)
        subprocess.run([sys.executable, "-I", str(Path(__file__).resolve().parent / "html2txt.py"), str(hp), str(out)], check=True)
        if len(out.read_text(errors="replace").split()) < 1500:
            raise ValueError("html too short")
    except Exception:  # noqa: BLE001
        src = "pdf"
        try:
            out.write_text(from_pdf(get(f"https://arxiv.org/pdf/{aid}"))); time.sleep(1)
        except Exception as e:  # noqa: BLE001
            print(aid, "FAILED", e); continue
    print(aid, src, len(out.read_text(errors="replace").split()))
