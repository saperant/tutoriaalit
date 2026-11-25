# Arkkitehtuurin mallinnus. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := arkkitehtuurin-tutkiminen
KIELI   := projekti
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat tuotetaan skriptillä kuvat/piirra.py esimerkkien funktioilla,
# luvun 2 jäljistä ja luvun 6 ydinmallin intervalleista; kuvat
# commitoidaan.
.PHONY: kuvat
kuvat:
	esimerkit/testaa.sh 02-kuormat 06-ydin
	PYTHONDONTWRITEBYTECODE=1 python3 kuvat/piirra.py kuvat \
	    esimerkit/build/02-kuormat esimerkit/build/06-ydin/intervallit.txt
