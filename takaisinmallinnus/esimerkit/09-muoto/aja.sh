#!/usr/bin/env bash
# Tuntemattoman tiedostomuodon selvittäminen.
source ./yhteinen.sh

"$CC" -std=c17 -O2 -Wall -Wextra -Werror tallenna.c -o tallenna
./tallenna
echo "koko: $(stat -c %s mittaukset.kmt) tavua"
otsikko "heksavedos, alku"
# @alku heksa
python3 tutki.py heksa mittaukset.kmt 0 0x60
# @loppu heksa
otsikko "entropia 32 tavun lohkoissa"
# @alku entropia
python3 tutki.py entropia mittaukset.kmt 32
# @loppu entropia
otsikko "merkkijonot"
python3 tutki.py merkkijonot mittaukset.kmt 4
otsikko "kokonaislukuehdokkaat"
# @alku luvut
python3 tutki.py luvut mittaukset.kmt
# @loppu luvut
otsikko "jäsennin"
# @alku jasenna
python3 jasenna.py mittaukset.kmt
# @loppu jasenna
