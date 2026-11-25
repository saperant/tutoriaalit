#!/usr/bin/env bash
# Staattinen ja jaettu kirjasto, viedyt symbolit, soname, ajonaikainen
# hakupolku, asennus ja pkg-config.
set -euo pipefail

# @alku staattinen
echo "== staattinen kirjasto: arkisto objektitiedostoista"
$CC -O2 -c lahde/tilasto.c -o tilasto.o
ar rcs libtilasto.a tilasto.o
ar t libtilasto.a
$CC -O2 -Ilahde lahde/main.c -L. -ltilasto -lm -o tilasto-staattinen
dyn() { readelf -d "$1" | awk '/NEEDED|RUNPATH|SONAME/ {print $2, $NF}'; }
dyn tilasto-staattinen
# @loppu staattinen

# @alku jaettu
echo "== jaettu kirjasto: -fPIC, soname ja versioskripti"
$CC -O2 -fPIC -c lahde/tilasto.c -o tilasto-pic.o
$CC -shared -Wl,-soname,libtilasto.so.1 \
    -Wl,--version-script=tilasto.map \
    tilasto-pic.o -lm -o libtilasto.so.1.2.0
ln -sf libtilasto.so.1.2.0 libtilasto.so.1
ln -sf libtilasto.so.1 libtilasto.so
nm -D --defined-only libtilasto.so.1.2.0 | cut -c18-
dyn libtilasto.so.1.2.0
# @loppu jaettu

# @alku haku
echo "== ohjelma, joka käyttää jaettua kirjastoa"
$CC -O2 -Ilahde lahde/main.c -L. -ltilasto -o tilasto-jaettu
./tilasto-jaettu < lahde/mittaukset.txt 2>&1 | head -n 1 \
    | grep -o 'libtilasto.so.1: cannot open shared object file' || true
echo "-- RUNPATH \$ORIGIN: kirjasto ohjelman vierestä"
# shellcheck disable=SC2016  # $ORIGIN on linkkerin, ei kuoren muuttuja
$CC -O2 -Ilahde lahde/main.c -L. -ltilasto -Wl,-rpath,'$ORIGIN' \
    -o tilasto-jaettu
dyn tilasto-jaettu
./tilasto-jaettu < lahde/mittaukset.txt | tail -n 1
# @loppu haku

# @alku asennus
echo "== asennus pakettia varten: PREFIX=/usr, DESTDIR=paketti"
make -s -f asennus.mk install PREFIX=/usr DESTDIR="$PWD/paketti"
(cd paketti && find . -type f | LC_ALL=C sort)
grep '^prefix' paketti/usr/lib/pkgconfig/tilasto.pc
# @loppu asennus

# @alku pkgconfig
echo "== asennus omaan hakemistoon ja pkg-config"
etuliite=$PWD/asennus
make -s -f asennus.mk install PREFIX="$etuliite"
export PKG_CONFIG_PATH=$etuliite/lib/pkgconfig
pkg-config --modversion tilasto
pkg-config --cflags --libs --static tilasto | sed 's/ *$//'
# shellcheck disable=SC2046  # liput on tarkoitus jakaa sanoiksi
$CC -O2 lahde/main.c $(pkg-config --cflags --libs --static tilasto) \
    -o tilasto-pkg
./tilasto-pkg < lahde/mittaukset.txt | tail -n 1
# @loppu pkgconfig
