#!/usr/bin/env bash
# Pinon ylivuoto: sanitoija, pinokanari ja kehyksen tutkiminen gdb:llä.
source ./yhteinen.sh

printf 'operaattori\n' > lyhyt.txt
printf '%040d\n' 0 | tr 0 A > pitka.txt

otsikko "AddressSanitizer"
"$CC" "${VAROITUKSET[@]}" "${SANITOIJAT[@]}" tunnus.c -o tunnus-asan
./tunnus-asan < lyhyt.txt
kaatuu ./tunnus-asan < pitka.txt

otsikko "pinokanari"
# @alku kanari
"$CC" "${VAROITUKSET[@]}" -O0 -fstack-protector-strong tunnus.c \
    -o tunnus-kanari
kaatuu ./tunnus-kanari < pitka.txt
# @loppu kanari
gdb_era kanari.gdb ./tunnus-kanari

otsikko "ilman kanaria"
# @alku ilman
"$CC" "${VAROITUKSET[@]}" -O0 -fno-stack-protector tunnus.c \
    -o tunnus-suojaamaton
kaatuu ./tunnus-suojaamaton < pitka.txt
gdb_era kehys.gdb ./tunnus-suojaamaton
# @loppu ilman

otsikko "korjattu rajapinta"
./tunnus-asan korjattu < pitka.txt || tila $?
