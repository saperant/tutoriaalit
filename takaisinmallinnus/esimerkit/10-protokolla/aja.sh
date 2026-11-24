#!/usr/bin/env bash
# Protokollan päättely liikennekaappauksesta.
source ./yhteinen.sh

"$CC" -std=c17 -O2 -Wall -Wextra -Werror laite.c -o laite
./laite
otsikko "kaappauksen alku"
# @alku heksa
od -A x -t x1 -N 48 kaappaus.bin
# @loppu heksa
otsikko "päättely"
# @alku paattele
python3 paattele.py kaappaus.bin
# @loppu paattele
