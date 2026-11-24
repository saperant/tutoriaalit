# Matematiikan perusteet ohjelmallisesti. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := matematiikan-perusteet
KIELI   := python
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat tuotetaan skriptillä kuvat/piirra.py; kuvat commitoidaan.
.PHONY: kuvat
kuvat:
	python3 kuvat/piirra.py kuvat
