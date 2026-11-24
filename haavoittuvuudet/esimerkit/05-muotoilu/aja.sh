#!/usr/bin/env bash
# Muotoilumerkkijonovirhe: varoitus, tietovuoto ja FORTIFY_SOURCE.
source ./yhteinen.sh

otsikko "kääntäjän varoitus"
"$CC" -std=c23 -Wall -Wformat=2 -c loki.c -o /dev/null 2>&1 |
    python3 varoitukset.py

# Haavoittuva versio käännetään ilman FORTIFY_SOURCEa ja varoitusta.
# @alku kaanna
SUOJAAMATON=(-std=c23 -O2 -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0
             -Wno-format-security)
"$CC" "${SUOJAAMATON[@]}" loki.c -o loki
# @loppu kaanna
otsikko "tavallinen viesti"
echo "kirjautuminen onnistui: aino" | ./loki
otsikko "muotoilumerkit viestissä"
# @alku vuoto
printf '%s\n' 'arvot: %lx %lx %lx' | ./loki |
    sed -E 's/\b[0-9a-f]+\b/X/g'
# shellcheck disable=SC2016  # $ on muotoilumerkki, ei muuttuja
for i in $(seq 1 40); do printf '%%%d$016lx\n' "$i"; done > haku.txt
if ./loki < haku.txt | grep -q 1d2c3b4a59687706; then
    echo "istuntoavain näkyy lokissa"
fi
# @loppu vuoto

otsikko "FORTIFY_SOURCE ja %n"
# @alku fortify
"$CC" -std=c23 -O2 -D_FORTIFY_SOURCE=2 -Wno-format-security loki.c \
    -o loki-fortify
echo 'tallenna %n' > kirjoitus.txt
kaatuu ./loki-fortify < kirjoitus.txt
# @loppu fortify

otsikko "korjattu"
"$CC" "${SUOJAAMATON[@]}" -DKORJATTU loki.c -o loki-korjattu
./loki-korjattu < kirjoitus.txt
if ! ./loki-korjattu < haku.txt | grep -q 1d2c3b4a59687706; then
    echo "istuntoavain ei näy lokissa"
fi
