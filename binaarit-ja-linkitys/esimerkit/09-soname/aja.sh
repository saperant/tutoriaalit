#!/usr/bin/env bash
# Soname, versionumerot ja binäärirajapinnan (ABI) rikkominen.
source ./yhteinen.sh
mkdir -p lib

# kirjasto OTSAKEHAKEMISTO VERSIO SONAME
kirjasto() {
    "$CC" "${CFLAGS[@]}" -fPIC -I"$1" -DVERSIO="\"$2\"" -c asetukset.c \
        -o "asetukset-$2.o"
    "$CC" -shared "asetukset-$2.o" -o "lib/libasetukset.so.$2" \
        -Wl,-soname,"$3"
}

# @alku v1
kirjasto v1 1.0 libasetukset.so.1
ln -sf libasetukset.so.1.0 lib/libasetukset.so.1   # ajonaikainen nimi
ln -sf libasetukset.so.1 lib/libasetukset.so       # linkityksen nimi
"$CC" "${CFLAGS[@]}" -Iv1 -c main.c -o main-v1.o
"$CC" main-v1.o -Llib -lasetukset -o vanha -Wl,-rpath,lib
readelf -d lib/libasetukset.so.1.0 | grep -oE 'SONAME.*' | tr -s ' '
readelf -d vanha | grep -oE 'NEEDED.*asetukset.*' | tr -s ' '
./vanha
# @loppu v1

otsikko "yhteensopiva päivitys 1.1"
# @alku v11
kirjasto v1 1.1 libasetukset.so.1
ln -sf libasetukset.so.1.1 lib/libasetukset.so.1
./vanha                                        # ei uudelleenlinkitystä
# @loppu v11

otsikko "virhe: ABI muuttui, soname ei"
# @alku rikki
kirjasto v2 2.0 libasetukset.so.1
ln -sf libasetukset.so.2.0 lib/libasetukset.so.1
./vanha
# @loppu rikki

otsikko "oikein: uusi soname"
# @alku oikein
ln -sf libasetukset.so.1.1 lib/libasetukset.so.1   # 1.1 takaisin
kirjasto v2 2.0 libasetukset.so.2
ln -sf libasetukset.so.2.0 lib/libasetukset.so.2
ln -sf libasetukset.so.2 lib/libasetukset.so
"$CC" "${CFLAGS[@]}" -Iv2 -c main.c -o main-v2.o
"$CC" main-v2.o -Llib -lasetukset -o uusi -Wl,-rpath,lib
./vanha
./uusi
# @loppu oikein
