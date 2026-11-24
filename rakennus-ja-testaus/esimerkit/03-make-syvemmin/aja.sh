#!/usr/bin/env bash
# Automaattiset riippuvuudet, käyttäjän liput ja rinnakkainen rakennus.
set -euo pipefail
m() { make --no-print-directory "$@"; }

echo "== ensimmäinen rakennus"
m
echo "== kääntäjän kirjoittama build/tilasto.d"
cat build/tilasto.d
echo "== tilasto.h muuttui: molemmat sitä lukevat käännetään"
touch lahde/tilasto.h
m
echo "== make -n V=1: komennot kokonaan, mitään ei tehdä"
touch lahde/main.c
m -n V=1 | grep -o '^gcc-14 .* -c'
echo "== optimointi pois käyttäjän lipuilla"
m siivoa > /dev/null
m CFLAGS=-O0 build/tilasto.o
echo "== rinnakkainen rakennus puhtaalta pöydältä"
m siivoa > /dev/null
m -j4 > /dev/null
objekteja=(build/*.o)
ohjelma=$(test -x build/tilasto && echo on)
echo "objekteja: ${#objekteja[@]}, ohjelma: $ohjelma"
m testaa | tail -n 1
