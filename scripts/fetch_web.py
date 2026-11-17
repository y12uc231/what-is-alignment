"""Fetch a non-arXiv source (blog post, paper PDF, system card) into fulltext/<slug>.txt.

Usage: python -I fetch_web.py SLUG URL   (PDF urls go through pypdf; HTML through html2txt)
"""
import io, subprocess, sys, urllib.request
from pathlib import Path

ROOT = Path.cwd()
FT = ROOT / "fulltext"; (FT / "html").mkdir(parents=True, exist_ok=True)
slug, url = sys.argv[1], sys.argv[2]
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research survey reader)"})
data = urllib.request.urlopen(req, timeout=60).read()
out = FT / f"{slug}.txt"
if data[:5] == b"%PDF-":
    from pypdf import PdfReader
    out.write_text("\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(data)).pages))
else:
    hp = FT / "html" / f"{slug}.html"; hp.write_bytes(data)
    subprocess.run([sys.executable, "-I", str(Path(__file__).resolve().parent / "html2txt.py"), str(hp), str(out)], check=True)
print(slug, len(out.read_text(errors="replace").split()), "words")
