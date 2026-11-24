#!/usr/bin/env bash
# Paikalliset, globaalit ja heikot symbolit.
source ./yhteinen.sh

for f in loki main oma_kohde; do
    "$CC" "${CFLAGS[@]}" -c "$f.c" -o "$f.o"
done

otsikko "loki.o"
symbolit loki.o rivinro muotoile loki_kohde loki snprintf __snprintf_chk

# @alku linkitys
otsikko "oletuskohde"
"$CC" main.o loki.o -o oletus && ./oletus
otsikko "sovelluksen kohde"
"$CC" main.o loki.o oma_kohde.o -o oma && ./oma
# @loppu linkitys

otsikko "lopullisen ohjelman loki_kohde"
symbolit oletus loki_kohde
symbolit oma loki_kohde
