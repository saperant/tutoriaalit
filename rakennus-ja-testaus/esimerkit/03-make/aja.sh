#!/usr/bin/env bash
# Make rakentaa vain sen, mikä on vanhentunut: kohde on vanhentunut, jos
# jokin sen riippuvuuksista on muuttunut kohteen jälkeen.
set -euo pipefail
m() { make --no-print-directory "$@"; }

echo "== ensimmäinen rakennus"
m
echo "== heti uudelleen"
m
echo "== tilasto.c muuttui"
touch lahde/tilasto.c
m
echo "== tilasto.h muuttui"
touch lahde/tilasto.h
m
echo "== testaa"
m testaa
# @alku verkko
echo "== riippuvuusverkko Maken tietokannasta"
m -pn | ./verkko.sh > uusi.dot
diff -u verkko.dot uusi.dot   # kirjan kuva vastaa Makefileä
echo "riippuvuuksia: $(grep -c -e '->' uusi.dot)"
echo "otsakkeesta tilasto.h: $(grep -c 'tilasto\.h' uusi.dot || true)"
# @loppu verkko
