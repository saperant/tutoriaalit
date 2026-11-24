#!/usr/bin/env bash
# Symbolien versiointi: kaksi toteutusta samalle nimelle.
source ./yhteinen.sh
mkdir -p lib
"$CC" "${CFLAGS[@]}" -c main.c -o main.o

dynsymbolit() {
    readelf --dyn-syms -W "$1" | grep -oE 'vertaa_tunnus@+TUNNUS_[0-9]' |
        sort -u
}

otsikko "versio 1 ja sitä vasten linkitetty ohjelma"
# @alku v1
"$CC" "${CFLAGS[@]}" -fPIC -shared tunnus-v1.c -o lib/libtunnus.so \
    -Wl,--version-script=tunnus-v1.map
"$CC" main.o -Llib -ltunnus -o vanha -Wl,-rpath,lib
dynsymbolit lib/libtunnus.so
dynsymbolit vanha
./vanha
# @loppu v1

otsikko "versio 2: vanha ohjelma säilyttää vanhan toiminnan"
# @alku v2
"$CC" "${CFLAGS[@]}" -fPIC -shared tunnus-v2.c -o lib/libtunnus.so \
    -Wl,--version-script=tunnus-v2.map
dynsymbolit lib/libtunnus.so
./vanha
"$CC" main.o -Llib -ltunnus -o uusi -Wl,-rpath,lib
dynsymbolit uusi
./uusi
# @loppu v2
