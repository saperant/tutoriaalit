# Tietokonearkkitehtuuri. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := tietokonearkkitehtuuri
KIELI   := cpp
RAKENNE := taito
include ../yhteiset/paketti.mk

# Liukuhihnakaaviot tuotetaan simulaattorin testatusta tulosteesta.
testaa: tarkista-kaaviot
.PHONY: tarkista-kaaviot
tarkista-kaaviot:
	@python3 kaaviot/tee.py --tarkista
