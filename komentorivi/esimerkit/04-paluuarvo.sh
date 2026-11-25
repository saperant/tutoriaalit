#!/usr/bin/env bash
# Paluuarvo ja komentojen ketjutus sen perusteella.
set -euo pipefail
export LC_ALL=C

printf 'palvelu käynnistyi\nvirhe: levy täynnä\n' > loki.txt

# @alku paluuarvo
grep -q 'virhe' loki.txt
echo "grep löysi: paluuarvo $?"
grep -q 'virhe' loki.txt && echo "löytyi (paluuarvo 0)"
grep -q 'varoitus' loki.txt || echo "ei löytynyt (paluuarvo $?)"
ls puuttuu.txt 2> /dev/null || echo "ls epäonnistui (paluuarvo $?)"
# @loppu paluuarvo
