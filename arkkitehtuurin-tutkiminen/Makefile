# Arkkitehtuurin mallinnus. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := arkkitehtuurin-tutkiminen
KIELI   := projekti
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat tuotetaan skriptillä kuvat/piirra.py luvun 2 jäljistä; kuvat
# commitoidaan.
.PHONY: kuvat
kuvat:
	esimerkit/testaa.sh 02-kuormat
	PYTHONDONTWRITEBYTECODE=1 python3 kuvat/piirra.py kuvat \
	    esimerkit/build/02-kuormat
