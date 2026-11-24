#!/usr/bin/env bash
# Staattinen kirjasto eli arkisto ja linkitysjärjestys.
source ./yhteinen.sh

for f in keskiarvo hajonta mediaani main; do
    "$CC" "${CFLAGS[@]}" -c "$f.c" -o "$f.o"
done

# @alku arkisto
ar rcs libtilasto.a keskiarvo.o hajonta.o mediaani.o
ar t libtilasto.a
# @loppu arkisto

otsikko "kirjasto ennen ohjelmaa"
# @alku vaara
virherivi "$CC" -L. -ltilasto -lm main.o -o tilasto
# @loppu vaara

otsikko "kirjasto ohjelman jälkeen"
# @alku oikein
"$CC" main.o -L. -ltilasto -lm -o tilasto -Wl,-Map=tilasto.map
./tilasto
# @loppu oikein

otsikko "arkistosta mukaan otetut jäsenet ja syy"
# @alku jasenet
# Linkkerikartan alussa luetellaan arkistosta otetut jäsenet ja
# viittaus, jonka vuoksi kukin otettiin.
sed -n '/^Archive member included/,/^Merging/p' tilasto.map |
    grep -o 'libtilasto\.a(.*' | tr -s ' '
# @loppu jasenet
symbolit tilasto mediaani keskiarvo hajonta

otsikko "kaksi määrittelyä samalle muuttujalle"
"$CC" "${CFLAGS[@]}" -c versio_a.c versio_b.c
# @alku kaksois
virherivi "$CC" -shared versio_a.o versio_b.o -o libversio.so
# @loppu kaksois
