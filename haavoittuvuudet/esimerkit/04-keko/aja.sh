#!/usr/bin/env bash
# Kekovirheet: ylivuoto, käyttö vapautuksen jälkeen ja kaksoisvapautus.
source ./yhteinen.sh

otsikko "kääntäjän varoitus"
# @alku varoitus
"$CC" -std=c23 -Wall -c istunnot.c -o /dev/null 2>&1 |
    python3 varoitukset.py
# @loppu varoitus
# Esimerkin virheet ovat tarkoituksellisia, joten varoitus ohitetaan.
LIPUT=("${VAROITUKSET[@]}" -Wno-use-after-free -O0)
"$CC" "${LIPUT[@]}" "${SANITOIJAT[@]}" istunnot.c -o istunnot-asan
"$CC" "${LIPUT[@]}" istunnot.c -o istunnot

for tapaus in ylivuoto vapautettu tupla; do
    otsikko "ASan: $tapaus"
    kaatuu ./istunnot-asan "$tapaus"
done

otsikko "keon metatiedot"
gdb_era metatiedot.gdb ./istunnot
otsikko "muistin uudelleenkäyttö"
./istunnot uudelleenkaytto
otsikko "glibc: kaksoisvapautus"
kaatuu ./istunnot tupla
