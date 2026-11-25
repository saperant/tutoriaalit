# Jatkuva integraatio ja toimitus. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := jatkuva-toimitus
KIELI   := projekti
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat tuotetaan skriptillä kuvat/piirra.py; kuvat commitoidaan.
.PHONY: kuvat
kuvat:
	python3 kuvat/piirra.py kuvat
