"""Which sense of "alignment" do accepted ML papers use? Rule-based count over ICLR/ICML/NeurIPS 2025-2026.

Population: accepted papers (Poster/Spotlight/Oral; main, position and datasets tracks; no workshops) whose TITLE matches \\balign.
Each paper gets the first matching sense in PRIORITY order, using title + abstract.
Writes data/term_usage/venue_senses.csv (counts) and notes/work/term_usage_samples.tsv (titles, for checking).

Usage: python -I scripts/term_usage_venues.py [VENUE_DIR]
"""
import csv
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

VDIR = Path(sys.argv[1] if len(sys.argv) > 1 else Path("venues"))
FILES = {"ICLR 2025": "iclr2025.json", "ICML 2025": "icml2025.json", "NeurIPS 2025": "nips2025.json",
         "ICLR 2026": "iclr2026.json", "ICML 2026": "icml2026.json", "NeurIPS 2026": "nips2026.json"}

ACCEPTED = {"Poster", "Spotlight", "Oral"}

# Order matters: a paper is counted under the first sense whose pattern matches.
PRIORITY = [
    ("misalignment-of-goals", r"misalign|alignment[- ]faking|deceptive alignment|schem|reward hack|specification gaming|"
                              r"goal misgeneral|sycophan|sandbag|superalignment|weak-to-strong|scalable oversight|"
                              r"\bhonest|decepti|power-seeking|corrigib|alignment audit"),
    ("safety-and-refusal", r"\bsafety\b|\bsafe\b|harmful|harmless|jailbreak|refus|red[- ]team|unsafe|toxic"),
    ("values-and-pluralism", r"\bvalues?\b|pluralis|cultur|moral|ethic|societ|democra|diverse preferences|"
                             r"population|personaliz|individual preferences"),
    ("preference-optimization", r"preference|rlhf|\bdpo\b|human feedback|reward model|policy optimization|"
                                r"instruction[- ]tun|instruction following|chat model|post-training|fine-tun"),
    ("representation-or-modality", r"modal|vision|visual|image|video|audio|speech|domain|feature|representation|"
                                   r"distribution|embedding|cross-lingual|token|layer|graph|molecul|protein|"
                                   r"\b3d\b|point cloud|sequence alignment|time[- ]series|temporal|spatial|"
                                   r"semantic|text-to-image|diffusion|latent|manifold|geometr|camera|scene|"
                                   r"brain|neural data|cell|gene|clip\b"),
]


def sense(title, abstract):
    t = (title + " " + abstract).lower()
    for name, pat in PRIORITY:
        if re.search(pat, t):
            return name
    return "other"


def main():
    rows, samples = [], []
    for venue, fn in FILES.items():
        papers = [p for p in json.load(open(VDIR / fn))
                  if p.get("status") in ACCEPTED and p.get("track", "main") in ("main", "Position", "Datasets & Benchmarks", "Evaluations & Datasets")]
        hits = [p for p in papers if re.search(r"\balign", p.get("title", ""), re.I)]
        c = Counter(sense(p.get("title", ""), p.get("abstract", "") or "") for p in hits)
        rows.append({"venue": venue, "accepted_total": len(papers), "align_in_title": len(hits), **c})
        for p in hits:
            samples.append((venue, sense(p.get("title", ""), p.get("abstract", "") or ""), p.get("title", "")))
    names = [n for n, _ in PRIORITY] + ["other"]
    out = Path("data/term_usage"); out.mkdir(parents=True, exist_ok=True)
    with open(out / "venue_senses.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["venue", "accepted_total", "align_in_title", *names])
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, 0) for k in w.fieldnames})
    random.seed(0)
    Path("notes/work").mkdir(parents=True, exist_ok=True)
    with open("notes/work/term_usage_samples.tsv", "w") as f:
        for n in names:
            pool = [s for s in samples if s[1] == n]
            for v, s, t in random.sample(pool, min(25, len(pool))):
                f.write(f"{s}\t{v}\t{t}\n")
    tot = Counter()
    for r in rows:
        print(r["venue"], r["accepted_total"], r["align_in_title"], {n: r.get(n, 0) for n in names})
        for n in names:
            tot[n] += r.get(n, 0)
    allh = sum(tot.values())
    print("ALL", allh, {n: f"{tot[n]} ({100 * tot[n] / allh:.0f}%)" for n in names})


if __name__ == "__main__":
    main()
