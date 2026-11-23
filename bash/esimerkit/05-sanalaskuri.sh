#!/usr/bin/env bash
# Laskee HTTP-tilakoodien esiintymät lokista assosiatiivisella
# taulukolla ja tulostaa ne yleisimmästä harvinaisimpaan.
set -euo pipefail
export LC_ALL=C

# @alku laskenta
declare -A maarat=()
puuttuvat=()
while read -r _ _ polku koodi _; do
    [[ $koodi =~ ^[1-5][0-9][0-9]$ ]] || continue
    maarat[$koodi]=$(( ${maarat[$koodi]:-0} + 1 ))
    if [[ $koodi == 404 ]]; then
        puuttuvat+=("$polku")
    fi
done
# @loppu laskenta

# @alku tulostus
for koodi in "${!maarat[@]}"; do
    printf '%s %d\n' "$koodi" "${maarat[$koodi]}"
done | sort -k2,2nr -k1,1
printf 'puuttuvat sivut: %s\n' "${puuttuvat[*]}"
# @loppu tulostus

# @alku olemassaolo
if [[ -v maarat[500] ]]; then
    echo "palvelinvirheitä: ${maarat[500]}"
fi
[[ -v maarat[418] ]] || echo "teepannuja ei havaittu"
# @loppu olemassaolo
