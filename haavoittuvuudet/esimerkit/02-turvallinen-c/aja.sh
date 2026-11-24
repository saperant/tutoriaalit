#!/usr/bin/env bash
# Turvallinen C: koon laskenta, etumerkit, ylivuodot ja analysaattorit.
source ./yhteinen.sh

otsikko "koon laskenta"
"$CC" "${VAROITUKSET[@]}" koko.c -o koko
# @alku koko
./koko 1000
./koko 1152921504606846977
# @loppu koko
./koko -1 || tila $?

otsikko "etumerkillinen pituus"
"$CC" "${VAROITUKSET[@]}" "${SANITOIJAT[@]}" pituus.c -o pituus
"$CC" "${VAROITUKSET[@]}" "${SANITOIJAT[@]}" -DKORJATTU pituus.c \
    -o pituus-korjattu
# @alku pituus
printf '\x00\x05hei!!' | ./pituus
printf '\xff\xffhei!!' > negatiivinen.bin
kaatuu ./pituus < negatiivinen.bin
./pituus-korjattu < negatiivinen.bin || tila $?
# @loppu pituus

otsikko "etumerkillinen ylivuoto"
"$CC" "${VAROITUKSET[@]}" "${SANITOIJAT[@]}" summa.c -o summa
"$CC" "${VAROITUKSET[@]}" "${SANITOIJAT[@]}" -DKORJATTU summa.c \
    -o summa-korjattu
# @alku summa
kaatuu ./summa 2147483640
./summa-korjattu 2147483640
# @loppu summa

otsikko "kääntäjän varoitukset"
# @alku varoitukset
"$CC" -std=c23 -Wall -Wextra -Wconversion -c asetukset.c \
    -o /dev/null 2>&1 | python3 varoitukset.py
# @loppu varoitukset
otsikko "GCC:n staattinen analyysi"
# @alku analyzer
"$CC" -std=c23 -fanalyzer -c asetukset.c -o /dev/null 2>&1 |
    python3 varoitukset.py
# @loppu analyzer
otsikko "clang-tidy"
# @alku tidy
clang-tidy-20 --quiet asetukset.c -- -std=c23 2> /dev/null |
    python3 varoitukset.py
# @loppu tidy
