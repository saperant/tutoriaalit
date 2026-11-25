# Korkean tason synteesi. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := hls
KIELI   := projekti
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat tuotetaan skriptillä kuvat/piirra.py; kuvat commitoidaan.
.PHONY: kuvat
kuvat:
	PYTHONDONTWRITEBYTECODE=1 python3 kuvat/piirra.py kuvat
