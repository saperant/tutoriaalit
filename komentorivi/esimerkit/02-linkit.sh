#!/usr/bin/env bash
# Kova ja symbolinen linkki sekä tiedoston korvaaminen.
set -euo pipefail
export LC_ALL=C

# @alku linkit
echo "versio 1" > asetukset.conf
ln asetukset.conf kova.conf
ln -s asetukset.conf symbolinen.conf
stat -c '%h linkkiä: %n' asetukset.conf
readlink symbolinen.conf
# @loppu linkit

# @alku muutos
echo "versio 2" > asetukset.conf     # sama inode, sisältö vaihtuu
cat kova.conf symbolinen.conf
rm asetukset.conf
cat kova.conf
cat symbolinen.conf 2> /dev/null || echo "symbolinen linkki on rikki"
# @loppu muutos

# @alku korvaus
echo "versio 3" > uusi.conf
cp kova.conf toinen.conf
ln -f toinen.conf kova2.conf
mv uusi.conf toinen.conf             # uusi inode nimelle toinen.conf
cat toinen.conf kova2.conf
# @loppu korvaus
