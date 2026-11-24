#!/usr/bin/env bash
# Kääntäjän tuottamien rakenteiden tunnistaminen.
source ./yhteinen.sh

"$CC" -std=c17 -O1 -fno-inline -Wall -Wextra -Werror ohjaus.c -o ohjaus
./ohjaus
for funktio in luokka hinnoittele varaston_arvo lavan_paino pituus; do
    otsikko "$funktio"
    purku ohjaus "$funktio"
done
otsikko "automaattinen tunnistus"
# @alku tunnista
python3 tunnista.py ohjaus luokka hinnoittele varaston_arvo \
    lavan_paino pituus
# @loppu tunnista
