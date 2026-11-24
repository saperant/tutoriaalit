#!/usr/bin/env bash
# Dynaaminen analyysi gdb:llä eräajona.
source ./yhteinen.sh

"$CC" -std=c23 -O1 -Wall -Wextra -Werror tilaus.c -o tilaus
./tilaus
for skripti in argumentit muuta jaljita vahti; do
    otsikko "$skripti.gdb"
    # @alku aja
    gdb_era "$skripti.gdb" ./tilaus
    # @loppu aja
    grep -E 'alennuskoodi' ohjelma.txt
done
