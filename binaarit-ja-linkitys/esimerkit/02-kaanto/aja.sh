#!/usr/bin/env bash
# Käännös ja linkitys erikseen: kaksi objektitiedostoa, yksi ohjelma.
source ./yhteinen.sh

# @alku vaiheet
"$CC" "${CFLAGS[@]}" -c laskin.c -o laskin.o   # vain käännös
"$CC" "${CFLAGS[@]}" -c main.c -o main.o
"$CC" main.o laskin.o -o laskin                 # vain linkitys
./laskin
# @loppu vaiheet

otsikko "laskin.o"
symbolit laskin.o loppusumma alenna
otsikko "main.o"
symbolit main.o main loppusumma printf __printf_chk
otsikko "tiedostotyypit"
# @alku tyypit
for f in laskin.o laskin; do
    printf '%s: %s\n' "$f" "$(readelf -h "$f" | awk -F: '/Type:/ {
        sub(/^ +/, "", $2); print $2 }')"
done
# @loppu tyypit
