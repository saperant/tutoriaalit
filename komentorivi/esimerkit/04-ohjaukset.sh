#!/usr/bin/env bash
# shellcheck disable=SC2012  # ls-tuloste on tässä tarkoituksella
# Tuloste- ja virhevirran ohjaaminen. ls kirjoittaa löytyneet
# tiedostot tulosteeseen ja virheet virhevirtaan.
set -euo pipefail
export LC_ALL=C
touch olemassa.txt

# @alku erikseen
ls olemassa.txt puuttuu.txt > tulos.txt 2> virheet.txt || true
cat tulos.txt
cat virheet.txt
# @loppu erikseen

# @alku yhdessa
ls olemassa.txt puuttuu.txt > kaikki.txt 2>&1 || true
wc -l < kaikki.txt
# @loppu yhdessa

# @alku jarjestys
ls olemassa.txt puuttuu.txt 2>&1 > vain-tulos.txt | sed 's/^/>> /' \
    || true
cat vain-tulos.txt
# @loppu jarjestys
