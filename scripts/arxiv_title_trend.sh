#!/bin/bash
# Title-phrase counts per calendar year on arXiv (cs.CL, cs.LG, cs.AI, cs.CV), 2019-2026 (2026 to Nov 17).
PY=${PY:-python3}
CATS='(cat:cs.CL OR cat:cs.LG OR cat:cs.AI OR cat:cs.CV)'
declare -a Q=(
 'all_align|ti:align*'
 'misalign|ti:misalign*'
 'safety_alignment|ti:"safety alignment"'
 'preference_alignment|ti:"preference alignment"'
 'human_preferences|ti:"human preferences"'
 'value_alignment|ti:"value alignment"'
 'ai_alignment|ti:"AI alignment"'
 'cross_modal_alignment|(ti:"cross-modal alignment" OR ti:"vision-language alignment" OR ti:"modality alignment")'
)
OUT=data/term_usage/arxiv_title_phrases.tsv
echo -e "series\tyear\tcount" > $OUT
for item in "${Q[@]}"; do
  name=${item%%|*}; q=${item#*|}
  for y in 2019 2020 2021 2022 2023 2024 2025 2026; do
    a=${y}0101; b=${y}1231; [ $y = 2026 ] && b=20261117
    c=$($PY -I scripts/arxiv_search.py count "($q) AND $CATS" $a $b 2>/dev/null)
    echo -e "$name\t$y\t$c" >> $OUT
    sleep 6
  done
done
echo done
