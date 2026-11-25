# EDA-työkaluketjujen automatisointi. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := eda-skriptaus
KIELI   := projekti
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat tuotetaan skriptillä kuvat/piirra.py; kuvat commitoidaan.
.PHONY: kuvat
kuvat:
	python3 kuvat/piirra.py kuvat
