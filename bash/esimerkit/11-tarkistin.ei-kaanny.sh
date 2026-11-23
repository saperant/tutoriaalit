#!/usr/bin/env bash
# Tyypillisiä virheitä, jotka ShellCheck löytää ennen ajoa. Rivit,
# joilla on merkintä @virhe, ovat virheelliset; korjattu versio on
# kunkin alla.
set -euo pipefail

touch 'kesän raportti.txt' muistio.txt
# @alku virheet
for t in $(ls ./*.txt); do echo "$t"; done          # @virhe SC2045
for t in ./*.txt; do echo "käsitellään: ${t#./}"; done

hakemisto=${1:-varmuuskopio}
cd $hakemisto 2> /dev/null && echo "siirrytty"      # @virhe SC2086
cd "$hakemisto" 2> /dev/null || echo "hakemistoa ei ole"

valinta=
[ -n $valinta ] && echo "valittu: $valinta"         # @virhe SC2070
[[ -n $valinta ]] || echo "ei valintaa"
# @loppu virheet
