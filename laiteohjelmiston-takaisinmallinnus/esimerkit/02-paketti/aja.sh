#!/usr/bin/env bash
# Päivityspaketin rakenteen selvittäminen: heksavedos, entropia,
# merkkijonot, kenttien tulkinta, tarkisteet ja edestakainen purku.
source ./yhteinen.sh
paketti=$LAITE/lt100-2.4.1.lt1

otsikko "heksavedos: alku"
# @alku vedos
python3 heksa.py "$paketti" 0 0x60
# @loppu vedos
otsikko "entropia 512 tavun lohkoissa"
# @alku entropia
python3 entropia.py "$paketti"
# @loppu entropia
otsikko "merkkijonot (siirtymä, teksti)"
# @alku merkkijonot
strings -n 12 -t x "$paketti" | head -8
# @loppu merkkijonot
otsikko "otsakkeen sanat"
# @alku sanat
python3 sanat.py "$paketti" 0 0x50
# @loppu sanat

# @alku tarkisteet
koko=$(wc -c < "$paketti")
sov=$(sana "$paketti" 0x28)
aset=$(sana "$paketti" 0x38)
res=$(sana "$paketti" 0x48)
python3 tarkistehaku.py "$paketti" --kentat 0x18 0x2c 0x3c 0x4c \
    --alueet "koko:0:$koko" otsake:0:0x20 "sovellus:0x50:$sov" \
    "asetukset:$((0x50 + sov)):$aset" \
    "resurssit:$((0x50 + sov + aset)):$res"
# @loppu tarkisteet
otsikko "purku ja uudelleenkokoaminen"
# @alku edestakaisin
python3 lt1.py nayta "$paketti"
python3 lt1.py pura "$paketti" osat
python3 lt1.py kokoa osat uusi.lt1
cmp "$paketti" uusi.lt1 && echo "uusi.lt1 on tavulleen sama"
head -3 osat/osio2.purettu
# @loppu edestakaisin
