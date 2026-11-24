# Tietoverkot. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := tietoverkot
KIELI   := python bash
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kirjan sekvenssikaaviot tuotetaan testatuista tulosteista.
testaa: tarkista-kaaviot
.PHONY: tarkista-kaaviot
tarkista-kaaviot:
	@python3 kaaviot/tee.py --tarkista
