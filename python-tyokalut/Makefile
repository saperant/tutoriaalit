# Python työkaluohjelmointiin. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := python-tyokalut
KIELI   := python
RAKENNE := taito
include ../yhteiset/paketti.mk

# Luvun 9 kuva tuotetaan esimerkillä ja luvun 8 kuva skriptillä
# kuvat/piirra.py esimerkin 08-analyysi funktioilla; kuvat commitoidaan.
.PHONY: kuvat
kuvat:
	python3 esimerkit/09-kuvaaja.py kuvat/mittaus.png
	python3 kuvat/piirra.py kuvat
