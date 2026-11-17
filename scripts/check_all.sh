#!/bin/bash
# Run every gate from the repository root. Needs the full texts in fulltext/ (see README).
set -u; PY=${PY:-python3}; rc=0
$PY -I scripts/verify_corpus.py || rc=1
$PY -I scripts/verify_reads.py | tail -1
$PY -I scripts/verify_cards.py --quiet | tail -1 || rc=1
$PY -I scripts/check_doc_quotes.py || rc=1
$PY -I scripts/check_cites.py || rc=1
$PY -I scripts/build_catalogue.py || rc=1
exit $rc
