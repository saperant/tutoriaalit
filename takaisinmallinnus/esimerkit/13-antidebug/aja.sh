#!/usr/bin/env bash
# Debuggerin havaitseminen ja havaitsemisen ohittaminen.
source ./yhteinen.sh

"$CC" -std=c23 -O2 -Wall -Wextra -Werror suojattu.c -o suojattu
otsikko "ilman debuggeria"
./suojattu
otsikko "strace ja gdb havaitaan"
strace -o /dev/null ./suojattu || echo "paluuarvo $?"
gdb -q -batch -nx -ex 'run > ohjelma.txt' ./suojattu > /dev/null 2>&1
cat ohjelma.txt
otsikko "ohita-pid.gdb: ensimmäinen tarkistus ohitettu"
gdb_era ohita-pid.gdb ./suojattu
cat ohjelma.txt
otsikko "ohita-kaikki.gdb: päätösfunktio ohitettu"
gdb_era ohita-kaikki.gdb ./suojattu
cat ohjelma.txt
otsikko "pysyvä paikkaus tiedostoon"
# @alku paikkaa
python3 paikkaa.py suojattu paikattu main debuggeri_havaittu
purku paikattu main | grep -A2 'xor eax,eax'
{ cmp -l suojattu paikattu || true; } | wc -l | sed 's/$/ tavua muuttui/'
gdb -q -batch -nx -ex 'run > ohjelma.txt' ./paikattu > /dev/null 2>&1
cat ohjelma.txt
# @loppu paikkaa
