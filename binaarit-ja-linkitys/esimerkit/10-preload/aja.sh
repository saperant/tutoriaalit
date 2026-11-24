#!/usr/bin/env bash
# LD_PRELOAD: oma kirjasto ladataan ennen muita ja sen symbolit voittavat.
source ./yhteinen.sh
echo "nopeus=120" > yleinen.conf

"$CC" "${CFLAGS[@]}" main.c -o lukija
# @alku preload
"$CC" "${CFLAGS[@]}" -fPIC -shared tiedostomittari.c \
    -o libtiedostomittari.so -ldl
./lukija
LD_PRELOAD=./libtiedostomittari.so ./lukija > tuloste.txt 2> mittari.txt
cat tuloste.txt mittari.txt
# @loppu preload
