#!/usr/bin/env bash
# Välilyönnit ja viiva tiedostonimien alussa.
set -euo pipefail
export LC_ALL=C

# @alku nimet
touch -- '-r' 'vuosi raportti.txt' 'kuukausi.txt'
ls
rm -- -r                     # tai: rm ./-r
for f in *.txt; do
    printf '[%s]\n' "$f"
done
# @loppu nimet

# @alku virhe
cat vuosi raportti.txt 2>&1 || true
# @loppu virhe
