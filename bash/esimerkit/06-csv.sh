#!/usr/bin/env bash
# Lukee tilausrivit CSV-muodossa (otsikkorivi, pilkkuerotin), validoi
# rivit ja laskee summat asiakkaittain sentteinä.
set -euo pipefail
export LC_ALL=C

# @alku lukeminen
declare -A summat=()
rivinro=0
IFS= read -r _otsikko                  # ohitetaan otsikkorivi
while IFS=, read -r tilaus asiakas maara hinta; do
    rivinro=$((rivinro + 1))
    if ! [[ $maara =~ ^[0-9]+$ && $hinta =~ ^[0-9]+\.[0-9]{2}$ ]]; then
        printf 'rivi %d hylätty: %s\n' "$rivinro" "$tilaus" >&2
        continue
    fi
    sentit=$(( 10#${hinta/./} * maara ))
    summat[$asiakas]=$(( ${summat[$asiakas]:-0} + sentit ))
done
# @loppu lukeminen

# @alku tulostus
for asiakas in "${!summat[@]}"; do
    s=${summat[$asiakas]}
    printf '%-10s %6d.%02d\n' "$asiakas" $(( s / 100 )) $(( s % 100 ))
done | sort
# @loppu tulostus
