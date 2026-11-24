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
