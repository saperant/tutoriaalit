# Python-kielipaketti. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := python
KIELI   := python
RAKENNE := kieli
include ../yhteiset/paketti.mk

# Mittauskuvaajat tuotetaan skriptillä kuvat/piirra.py; kuvat commitoidaan.
.PHONY: kuvat
kuvat:
	python3 kuvat/piirra.py kuvat
