#!/usr/bin/env bash
# Yksikkötestit pienellä kehyksellä, valekello linkitysvaiheessa ja
# muistinvarauksen virhe --wrap-valitsimella.
set -euo pipefail
m() { make -s --no-print-directory "$@"; }

echo "== testit"
m testaa
echo "== tuotanto-ohjelma rakentuu oikeaa kelloa vasten"
m raportti
./raportti | sed -E 's/[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9:]{5}/<nyt>/'

echo "== virhe keskiarvossa: mitä testit kertovat"
sed -i 's|summa / (double)n|summa / (double)(n + 1)|' lahde/tilasto.c
m testit
./testit || echo "paluuarvo $?"
