# Kontit ja pilvi. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := kontit-ja-pilvi
KIELI   := projekti
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat tuotetaan skriptillä kuvat/piirra.py; kuvat commitoidaan.
.PHONY: kuvat
kuvat:
	python3 kuvat/piirra.py kuvat
