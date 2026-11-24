# Digitaalinen signaalinkasittely. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := dsp
KIELI   := python c
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat tuotetaan skriptilla kuvat/piirra.py; kuvat commitoidaan.
.PHONY: kuvat
kuvat:
	python3 kuvat/piirra.py kuvat
