#!/usr/bin/env bash
# Tiedostojen läpikäynti turvallisesti: glob ja nullglob, sekä find
# nollatavuerottimella mielivaltaisille nimille.
set -euo pipefail
export LC_ALL=C          # glob- ja lajittelujärjestys lokaalista riippumatta

mkdir -p data/arkisto
touch 'data/raportti 1.csv' data/raportti2.csv data/arkisto/vanha.csv \
      $'data/rivin\nvaihto.csv'

# @alku glob
shopt -s nullglob           # ei osumia -> tyhjä lista, ei kuviota itseään
for tiedosto in data/*.csv; do
    printf 'glob: %q\n' "$tiedosto"
done
for tiedosto in data/*.json; do
    echo "ei tulostu: $tiedosto"
done
# @loppu glob

# @alku find
maara=0
while IFS= read -r -d '' tiedosto; do
    maara=$((maara + 1))
done < <(find data -name '*.csv' -print0)
echo "find löysi $maara CSV-tiedostoa"
# @loppu find

# @alku cstyle
for (( i = 3; i > 0; i-- )); do
    printf '%d...' "$i"
done
echo 'käynnistys'
# @loppu cstyle
