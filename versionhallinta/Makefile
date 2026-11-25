# Versionhallinta (Git). Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := versionhallinta
KIELI   := bash
RAKENNE := taito
include ../yhteiset/paketti.mk

# Commit-verkkojen kuvat tuotetaan esimerkkien luomista repositorioista.
testaa: tarkista-kaaviot
.PHONY: tarkista-kaaviot
tarkista-kaaviot:
	@python3 kaaviot/tee.py --tarkista
