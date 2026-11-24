#!/usr/bin/env bash
# Symbolittoman ohjelman analyysi: funktioiden rajat, main ja
# kirjastofunktioiden tunnistus allekirjoituksilla.
source ./yhteinen.sh

# @alku kaanna
"$CC" -std=c17 -O2 -Wall -Wextra -Werror -c kirjasto.c -o kirjasto.o
"$CC" -std=c17 -O2 -Wall -Wextra -Werror ohjelma.c kirjasto.o -o ohjelma
strip -s -o ohjelma-s ohjelma
# @loppu kaanna
./ohjelma-s
otsikko "mitä riisuminen poisti"
# @alku riisuttu
for tiedosto in ohjelma ohjelma-s; do
    funktioita=$(nm "$tiedosto" 2>&1 | grep -c ' [Tt] ' || true)
    osioita=$(readelf -SW "$tiedosto" |
        grep -cE '\.(symtab|strtab|eh_frame) ')
    echo "$tiedosto: $funktioita funktiosymbolia, $osioita osiota" \
        "(.symtab, .strtab, .eh_frame)"
done
nm -D ohjelma-s | awk '$1 == "U" { sub(/@.*/, "", $2); print "tuonti:", $2 }'
# @loppu riisuttu
otsikko "_start (riisumattomasta ohjelmasta)"
purku ohjelma _start
otsikko "rajat, main ja allekirjoitukset"
# @alku tunnistus
python3 riisuttu.py ohjelma-s kirjasto.o ohjelma
# @loppu tunnistus
