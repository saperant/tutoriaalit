#!/usr/bin/env bash
# Optimointien tunnistaminen: -O0 ja -O2 rinnakkain.
source ./yhteinen.sh

# @alku kaanna
for taso in O0 O2 O3; do
    "$CC" -std=c17 "-$taso" -Wall -Wextra -Werror optimoi.c -o "optimoi-$taso"
done
# @loppu kaanna
./optimoi-O2
otsikko "käskyt ja kutsut"
# @alku vertaa
python3 vertaa.py optimoi-O0 optimoi-O2 etaisyys2 syt ilmoita skaalaa \
    summa8 jaa7 jaa10
# @loppu vertaa
for funktio in etaisyys2 syt ilmoita summa8; do
    otsikko "$funktio -O2"
    purku optimoi-O2 "$funktio"
done
otsikko "skaalaa -O3: vektoroitu silmukka"
# @alku vektori
purku optimoi-O3 skaalaa | sed -n '/movdqu/,/jne/p'
# @loppu vektori
echo "käskyjä: -O2 $(purku optimoi-O2 skaalaa | grep -vc '^<')," \
    "-O3 $(purku optimoi-O3 skaalaa | grep -vc '^<')"
# @loppu vektori
for funktio in jaa7 jaa10 jaa8 jaannos10; do
    otsikko "$funktio -O2"
    purku optimoi-O2 "$funktio"
done
otsikko "jakajat taikaluvuista"
# @alku taikaluku
python3 taikaluku.py optimoi-O2 jaa7 jaa10 jaannos10
# @loppu taikaluku
