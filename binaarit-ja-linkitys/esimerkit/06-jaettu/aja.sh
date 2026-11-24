#!/usr/bin/env bash
# Jaettu kirjasto: rakentaminen, linkitys ja löytäminen ajossa.
source ./yhteinen.sh
mkdir -p asennus/lib asennus/bin

# @alku rakennus
"$CC" "${CFLAGS[@]}" -fPIC -c yksikot.c -o yksikot.o
"$CC" -shared yksikot.o -o asennus/lib/libyksikot.so
"$CC" "${CFLAGS[@]}" -c main.c -o main.o
"$CC" main.o -Lasennus/lib -lyksikot -o asennus/bin/muunnin
# @loppu rakennus

otsikko "riippuvuudet (readelf -d)"
riippuvuudet() {
    readelf -d "$1" | grep -E 'NEEDED|RUNPATH|RPATH' |
        sed -E 's/.*\((NEEDED|RUNPATH|RPATH)\).*\[(.*)\]/\1 \2/'
}
riippuvuudet asennus/bin/muunnin

otsikko "ajo ilman hakupolkua"
# @alku ilman
if ! asennus/bin/muunnin 2> virhe.txt; then
    grep -o 'libyksikot.so: cannot open shared object file' virhe.txt
fi
ldd asennus/bin/muunnin | grep -o 'libyksikot.so => .*'
# @loppu ilman

otsikko "LD_LIBRARY_PATH"
# @alku ymparisto
LD_LIBRARY_PATH=asennus/lib asennus/bin/muunnin
# @loppu ymparisto

otsikko "RUNPATH ohjelman sijainnin mukaan"
# @alku runpath
# $ORIGIN on lataajan muuttuja, ei kuoren: lainausmerkit estävät
# laajentamisen.
# shellcheck disable=SC2016
"$CC" main.o -Lasennus/lib -lyksikot -o asennus/bin/muunnin \
    -Wl,-rpath,'$ORIGIN/../lib'
riippuvuudet asennus/bin/muunnin
asennus/bin/muunnin
# Asennushakemiston voi siirtää: polku on suhteessa ohjelmaan.
mv asennus siirretty && siirretty/bin/muunnin
# @loppu runpath
