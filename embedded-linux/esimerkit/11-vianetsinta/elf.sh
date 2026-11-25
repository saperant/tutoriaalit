#!/bin/sh
# Näyttää ohjelmatiedostoista ne tiedot, joista käynnistysvian syy
# selviää isännällä: arkkitehtuuri, tulkki ja tarvittavat kirjastot.
# Käyttö: elf.sh TIEDOSTO...
set -eu
# @alku tiedot
for tiedosto in "$@"; do
    echo "$(basename "$tiedosto"):"
    readelf -h "$tiedosto" | sed -n 's/^ *Machine: */  arkkitehtuuri: /p'
    readelf -l "$tiedosto" |
        sed -n 's/.*interpreter: \([^]]*\)\]/  tulkki: \1/p'
    readelf -d "$tiedosto" 2> /dev/null |
        sed -n 's/.*(NEEDED).*\[\(.*\)\]/  tarvitsee: \1/p'
done
# @loppu tiedot
