# Tiimit ja organisaatiomallit. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := tiimit-ja-organisaatiot
KIELI   := python
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat tuotetaan skriptillä kuvat/piirra.py; kuvat commitoidaan.
.PHONY: kuvat
kuvat:
	python3 kuvat/piirra.py kuvat
