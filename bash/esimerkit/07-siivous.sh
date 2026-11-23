#!/usr/bin/env bash
# Väliaikaiset resurssit siivotaan EXIT-ansalla, joka suoritetaan
# skriptin päättyessä millä tavalla tahansa: normaalisti, virheeseen
# (set -e) tai exit-komennolla.
set -euo pipefail

# @alku ansa
tyohak=$(mktemp -d)
siivoa() {
    local tila=$?
    rm -rf -- "$tyohak"
    echo "siivottu (tila $tila)"
}
trap siivoa EXIT
# @loppu ansa

# @alku tyo
printf 'rivi %d\n' 1 2 3 > "$tyohak/data.txt"
wc -l < "$tyohak/data.txt"
[[ -d $tyohak ]] && echo "työhakemisto olemassa"
# @loppu tyo
