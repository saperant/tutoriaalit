# Laiteohjelmiston takaisinmallinnus. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := laiteohjelmiston-takaisinmallinnus
KIELI   := projekti
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat tuotetaan skriptillä kuvat/piirra.py; kuvat commitoidaan.
.PHONY: kuvat
kuvat:
	python3 kuvat/piirra.py kuvat
