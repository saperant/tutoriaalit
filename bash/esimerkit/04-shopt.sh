#!/usr/bin/env bash
# shopt-asetukset, jotka muuttavat globien ja putkien toimintaa.
set -euo pipefail
export LC_ALL=C

mkdir -p lahde/ydin lahde/testit
touch lahde/paa.c lahde/ydin/jono.c lahde/ydin/jono.h lahde/testit/t_jono.c

# @alku shopt
shopt -s nullglob globstar extglob lastpipe

printf 'kaikki: %s\n' lahde/**/*.c
printf 'ei testit: %s\n' lahde/!(testit)/*.c

maara=0
printf '%s\n' lahde/**/*.h | while read -r _; do (( maara += 1 )); done
echo "otsikkotiedostoja: $maara"
# @loppu shopt
