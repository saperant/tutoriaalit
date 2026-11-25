#!/usr/bin/env bash
# Luvun 13 työkaluajot eräajoina:
#
#   ./13-tyokalut.sh gdb        gdb-istunto esimerkille 08-vektori
#   ./13-tyokalut.sh analyysi   GCC:n staattinen analyysi
#
# make tyokalut vertaa tulosteita tiedostoihin 13-gdb.tuloste ja
# 13-analyysi.tuloste.
set -euo pipefail
export LC_ALL=C DEBUGINFOD_URLS=
CC=${CC:-gcc-14}

# @alku gdb
gdb_istunto() {
    mkdir -p bin
    "$CC" -std=c23 -g -O0 08-vektori.c -o bin/13-vektori
    # -batch: suorita komennot ja lopeta; -nx: ei käyttäjän asetuksia.
    gdb -batch -nx \
        -ex 'break vektori_lisaa if v->koko == 4' \
        -ex 'run > /dev/null' \
        -ex 'bt' \
        -ex 'print arvo' \
        -ex 'print *v->data@v->koko' \
        -ex 'print v->kapasiteetti' \
        -ex 'finish' \
        -ex 'print v.kapasiteetti' \
        bin/13-vektori 2>&1
}
# @loppu gdb

# Muistiosoitteet ja ympäristön ilmoitukset (esim. kontin varoitus
# osoiteavaruuden satunnaistuksesta) vaihtelevat: ne poistetaan.
siisti() {
    grep -vE 'libthread_db|^warning: Error disabling|^$' \
        | sed -E 's/ at 0x[0-9a-f]+: / at /; s/0x[0-9a-f]{5,}/0x.../g' \
        | expand -t 8
}

# @alku analyysi
analyysi() {
    "$CC" -std=c23 -Wall -Wextra -fanalyzer -c -o /dev/null \
        -fdiagnostics-plain-output \
        -fdiagnostics-path-format=separate-events 13-analyysi.c 2>&1
}
# @loppu analyysi

# Rivit lyhennetään sivulle mahtuviksi: CWE-numero ja ehtojen
# selitykset pois.
lyhenna() {
    sed -E 's/ \[CWE-[0-9]+\]//; s/ \(when [^)]*\)//'
}

case ${1:-} in
gdb) gdb_istunto | siisti ;;
analyysi) analyysi | lyhenna ;;
*) echo "käyttö: $0 gdb|analyysi" >&2; exit 2 ;;
esac
