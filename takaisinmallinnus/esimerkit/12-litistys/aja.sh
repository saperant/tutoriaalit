#!/usr/bin/env bash
# Ohjausvuon litistyksen purku ja läpinäkymätön predikaatti.
source ./yhteinen.sh

"$CC" -std=c17 -O0 -Wall -Wextra -Werror luhn.c -o luhn
otsikko "tavallinen ja litistetty antavat saman tuloksen"
./luhn
otsikko "purun koko"
for funktio in luhn luhn_litistetty; do
    echo "$funktio: $(purku luhn "$funktio" | grep -vc '^<') käskyä"
done
otsikko "välittäjän alku"
# @alku valittaja
purku luhn luhn_litistetty |
    awk '/mov DWORD PTR \[rbp-0x4\],0x6b2f9c01/ { n = 1 } n && c++ < 9'
# @loppu valittaja
otsikko "palautettu tilakone"
# @alku litistys
python3 litistys.py luhn luhn_litistetty
# @loppu litistys
otsikko "läpinäkymätön predikaatti"
python3 predikaatti.py
