#!/usr/bin/env bash
# Ohjelman käynnistys: lataaja, aloituskohta ja alustusten järjestys.
source ./yhteinen.sh

otsikko "alustusten järjestys"
# @alku jarjestys
"$CC" "${CFLAGS[@]}" -fPIC -shared kirjasto.c -o libkirjasto.so
"$CC" "${CFLAGS[@]}" main.c -o ohjelma -L. -lkirjasto \
    -Wl,-rpath,"$PWD"
./ohjelma
# @loppu jarjestys

otsikko "lataaja ja aloituskohta"
# @alku lataaja
readelf -l ohjelma | grep -oE 'interpreter: [^]]+'
alku=$(readelf -h ohjelma | awk '/Entry point/ { print $NF }')
nm ohjelma | grep "^$(printf '%016x' "$alku") T" | sed 's/^.* /aloitus: /'
readelf -S -W ohjelma | sed -E 's/^ *\[ *[0-9]+\] //' |
    awk '$1 ~ /^\.(init|fini)(_array)?$/ { print $1 }'
# @loppu lataaja

otsikko "aputaulukko (auxv)"
# @alku auxv
LD_SHOW_AUXV=1 ./ohjelma | grep -E '^AT_(PAGESZ|ENTRY|EXECFN):' |
    sed -E 's/0x[0-9a-f]+/OSOITE/; s/(AT_EXECFN: +).*/\1(ohjelman polku)/'
# @loppu auxv
