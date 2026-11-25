#!/usr/bin/env bash
# shellcheck disable=SC2016,SC2086  # lainaamattomat muodot tarkoituksella
# Lainausmerkit: mitä kuori laajentaa missäkin.
set -euo pipefail
export LC_ALL=C

# @alku lainaus
nimi="vuosi raportti.txt"
echo 'luonnos' > "$nimi"
touch muistio.txt

echo 'Yksinkertaiset: $nimi ja *.txt sellaisenaan'
echo "Kaksinkertaiset: $nimi, $(wc -c < "$nimi") tavua, *.txt"
echo Lainaamaton: *.txt

printf '<%s>\n' $nimi
printf '<%s>\n' "$nimi"
echo "Kenoviiva poistaa merkityksen: \$nimi ja \"lainaus\""
# @loppu lainaus
