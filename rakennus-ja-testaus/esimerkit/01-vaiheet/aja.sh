#!/usr/bin/env bash
# Käännöksen vaiheet yksi kerrallaan: esikäsittely, käännös assemblyksi,
# kokoaminen objektitiedostoksi ja linkitys ohjelmaksi.
set -euo pipefail

# @alku esikasittely
echo "== 1. esikäsittely (cpp): makrot auki, kommentit pois"
$CC -E -P pinta.c
# @loppu esikasittely

# @alku kaannos
echo "== 2. käännös assemblyksi (-S): funktion käskyt"
$CC -O2 -S pinta.c -o - | sed -n '/^pinta_ala:/,/\.size/p' \
    | grep -Ev '^[[:space:]]*\.(cfi|size|p2align)' | expand -t 8
# @loppu kaannos

# @alku objektit
echo "== 3. kokoaminen objektitiedostoiksi (-c)"
$CC -std=c17 -c lahde/tilasto.c lahde/main.c
echo "-- tilasto.o: T = määritelty, t = paikallinen, U = puuttuu"
nm tilasto.o
echo "-- main.o (vain tilaston funktiot)"
nm main.o | grep -E ' (keskiarvo|keskihajonta|mediaani)$'
# @loppu objektit

# @alku linkitys
echo "== 4. linkitys: ilman matematiikkakirjastoa"
if ! $CC tilasto.o main.o -o tilasto 2> linkkeri.txt; then
    grep -o "undefined reference to \`sqrt'" linkkeri.txt
fi
echo "== 4. linkitys: -lm mukaan"
$CC tilasto.o main.o -lm -o tilasto
./tilasto < lahde/mittaukset.txt
# @loppu linkitys
