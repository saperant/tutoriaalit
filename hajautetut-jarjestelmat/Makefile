# Hajautetut järjestelmät. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := hajautetut-jarjestelmat
KIELI   := cpp
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat tuotetaan skriptillä kuvat/piirra.py; kuvat commitoidaan.
.PHONY: kuvat
kuvat:
	python3 kuvat/piirra.py kuvat
