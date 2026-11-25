#!/usr/bin/env bash
# Rakenteiden asettelu ABI:n mukaan: koot, tasaukset ja täyte.
source ./yhteinen.sh

# @alku asettelu
"$CC" "${CFLAGS[@]}" -Wpadded -Wno-error=padded -c main.c 2> varoitukset.txt
grep -oE "padding struct size to alignment boundary|padding struct to \
align '[a-z]+'" varoitukset.txt | sort | uniq -c | sed -E 's/^ +//'
"$CC" main.o -o asettelu
./asettelu
# @loppu asettelu

otsikko "tarkistus pysäyttää käännöksen"
# @alku tarkistus
if "$CC" "${CFLAGS[@]}" -c rikki.c 2> virhe.txt; then exit 1; fi
grep -oE 'static assertion failed: "[^"]+"' virhe.txt
# @loppu tarkistus
