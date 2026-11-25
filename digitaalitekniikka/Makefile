# Digitaalitekniikka. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := digitaalitekniikka
KIELI   := python systemverilog
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat tuotetaan skriptillä kuvat/piirra.py; kuvat ovat versionhallinnassa.
.PHONY: kuvat
kuvat:
	python3 kuvat/piirra.py kuvat
