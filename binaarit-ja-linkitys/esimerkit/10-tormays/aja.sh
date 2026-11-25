#!/usr/bin/env bash
# Kahden jaetun kirjaston symbolitörmäys ja sen korjaus.
source ./yhteinen.sh
"$CC" "${CFLAGS[@]}" -c main.c -o main.o
jaettu() { "$CC" "${CFLAGS[@]}" -fPIC -shared "$1" -o "$2"; }

otsikko "kaksi kirjastoa, sama julkinen nimi"
# @alku tormays
jaettu kuva.c libkuva.so
jaettu aani.c libaani.so
"$CC" main.o -L. -lkuva -laani -o ohjelma -Wl,-rpath,.
./ohjelma
# @loppu tormays

otsikko "sama ohjelma, kirjastot toisessa järjestyksessä"
"$CC" main.o -L. -laani -lkuva -o ohjelma2 -Wl,-rpath,.
./ohjelma2

otsikko "korjattu: sisäinen funktio piilotettu"
# @alku korjattu
jaettu aani-piilo.c libaani.so
./ohjelma
nm -D libaani.so | awk '$NF ~ /tarkista|lataa_aani/ { print $(NF - 1), $NF }'
# @loppu korjattu
