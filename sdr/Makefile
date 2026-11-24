# Ohjelmistoradio. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := sdr
KIELI   := python cpp
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat tuotetaan skriptilla kuvat/piirra.py; kuvat commitoidaan.
.PHONY: kuvat
kuvat:
	python3 kuvat/piirra.py kuvat
