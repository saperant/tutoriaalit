# Edistyneet algoritmit ja tietorakenteet. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := edistyneet-algoritmit
KIELI   := cpp
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kirjan kaaviot tuotetaan esimerkkien testatuista tulosteista.
testaa: tarkista-kaaviot
.PHONY: tarkista-kaaviot
tarkista-kaaviot:
	@python3 kaaviot/tee.py --tarkista
