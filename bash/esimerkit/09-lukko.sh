#!/usr/bin/env bash
# flock estää saman skriptin päällekkäiset ajot, esimerkiksi kun
# cron käynnistää uuden ajon ennen kuin edellinen on valmis.
set -euo pipefail

# @alku lukko
LUKKO=./synkronointi.lukko

aja_lukittuna() {
    local fd
    exec {fd}> "$LUKKO"
    if ! flock -n "$fd"; then
        echo "edellinen ajo on kesken, lopetetaan" >&2
        return 1
    fi
    echo "synkronoidaan ($1)"
    sleep 1                         # varsinainen työ
    echo "valmis ($1)"
}
# @loppu lukko

# @alku kokeilu
# Ensimmäinen ajo taustalle. Kun sen ensimmäinen rivi on luettu,
# lukko on varmasti sillä.
exec {ensimmainen}< <(aja_lukittuna ensimmäinen)
read -r -u "$ensimmainen" rivi && echo "$rivi"
aja_lukittuna toinen 2>&1 || echo "toinen ajo hylättiin"
cat <&"$ensimmainen"
# @loppu kokeilu
