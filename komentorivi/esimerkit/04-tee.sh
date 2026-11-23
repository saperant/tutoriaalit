#!/usr/bin/env bash
# tee tallentaa välituloksen ja jatkaa putkea.
set -euo pipefail
export LC_ALL=C
printf '%s\n' 340 12 1200 87 560 9 > vasteajat.txt

# @alku tee
sort -n vasteajat.txt | tee lajiteltu.txt | tail -n 2
wc -l < lajiteltu.txt
echo 2400 | tee -a vasteajat.txt > /dev/null
tail -n 1 vasteajat.txt
# @loppu tee
