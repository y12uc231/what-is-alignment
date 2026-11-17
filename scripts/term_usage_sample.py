"""Draw the random sample of 200 accepted-paper titles containing "align" that Section 8 labels.

Population: ICLR/ICML/NeurIPS 2025-2026 accepted papers (Poster/Spotlight/Oral; main, Position,
Datasets & Benchmarks, Evaluations & Datasets tracks) whose title matches \\balign (case-insensitive).
Writes data/term_usage/venue_population.jsonl and prints the sample (index, venue, title) in sample order.

Usage: python -I scripts/term_usage_sample.py [VENUE_DIR]
"""
import json
import random
import re
import sys
from pathlib import Path

VDIR = Path(sys.argv[1] if len(sys.argv) > 1 else Path("venues"))
FILES = {"ICLR 2025": "iclr2025.json", "ICML 2025": "icml2025.json", "NeurIPS 2025": "nips2025.json",
         "ICLR 2026": "iclr2026.json", "ICML 2026": "icml2026.json", "NeurIPS 2026": "nips2026.json"}
ACCEPTED = {"Poster", "Spotlight", "Oral"}
TRACKS = ("main", "Position", "Datasets & Benchmarks", "Evaluations & Datasets")
SEED = 20261117


def main():
    pop = []
    for venue, fn in FILES.items():
        for p in json.load(open(VDIR / fn)):
            if (p.get("status") in ACCEPTED and p.get("track", "main") in TRACKS
                    and re.search(r"\balign", p.get("title", ""), re.I)):
                pop.append({"venue": venue, "title": p["title"].strip()})
    with open("data/term_usage/venue_population.jsonl", "w") as f:
        for p in pop:
            f.write(json.dumps(p) + "\n")
    random.seed(SEED)
    for i, p in enumerate(random.sample(pop, 200)):
        print(f"{i}\t{p['venue']}\t{p['title']}")
    print(f"population {len(pop)}", file=sys.stderr)


if __name__ == "__main__":
    main()
