#!/usr/bin/env bash
# Taulukon perusoperaatiot: lukeminen tiedostosta, indeksit, viipaleet,
# poistaminen ja yhdistäminen merkkijonoksi.
set -euo pipefail

printf '%s\n' alfa beeta gamma delta epsilon > palvelimet.txt

# @alku mapfile
mapfile -t palvelimet < palvelimet.txt
echo "määrä:     ${#palvelimet[@]}"
echo "eka:       ${palvelimet[0]}"
echo "viimeinen: ${palvelimet[-1]}"
echo "viipale:   ${palvelimet[*]:1:2}"
# @loppu mapfile

# @alku poisto
unset 'palvelimet[2]'                   # jättää aukon indeksiin 2
echo "indeksit:  ${!palvelimet[*]}"
palvelimet=("${palvelimet[@]}")         # tiivistää indeksit
echo "tiivistetty: ${!palvelimet[*]}"
# @loppu poisto

# @alku yhdistys
yhdista() {
    local IFS=$1
    shift
    echo "$*"
}
echo "pilkuin:   $(yhdista , "${palvelimet[@]}")"
# @loppu yhdistys

# @alku suodatus
lyhyet=()
for p in "${palvelimet[@]}"; do
    (( ${#p} <= 5 )) && lyhyet+=("$p")
done
echo "lyhyet:    ${lyhyet[*]}"
# @loppu suodatus
