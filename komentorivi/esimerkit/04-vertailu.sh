#!/usr/bin/env bash
# Kahden listan vertailu prosessikorvauksella: kenellä on tunnus,
# vaikka hän ei ole enää henkilöstölistalla?
set -euo pipefail
export LC_ALL=C

printf '%s\n' matti kaisa laura pekka > henkilosto.txt
printf '%s\n' kaisa pekka olli matti root > tunnukset.txt

# @alku comm
comm -13 <(sort henkilosto.txt) <(sort tunnukset.txt)
# @loppu comm

# @alku diff
diff <(sort henkilosto.txt) <(sort tunnukset.txt) || true
# @loppu diff
