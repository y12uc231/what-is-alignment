#!/bin/bash
# Download ICLR/ICML/NeurIPS 2025-2026 accepted-paper lists from papercopilot/paperlists into venues/ (used by Section 8).
set -eu
mkdir -p venues && cd venues
for f in iclr/iclr2025 iclr/iclr2026 icml/icml2025 icml/icml2026 nips/nips2025 nips/nips2026; do
  n=$(basename $f)
  [ -s $n.json ] && head -c 20 $n.json | grep -q '^\[' && continue
  curl -sSL -m 600 -o $n.json "https://media.githubusercontent.com/media/papercopilot/paperlists/main/$f.json" || \
  curl -sSL -m 600 -o $n.json "https://raw.githubusercontent.com/papercopilot/paperlists/main/$f.json"
  echo "$n $(wc -c < $n.json) bytes"
done
