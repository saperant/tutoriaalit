# Algoritmit. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := algoritmit
KIELI   := c
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat tuotetaan skriptillä kuvat/piirra.py; kuvat commitoidaan.
.PHONY: kuvat
kuvat:
	python3 kuvat/piirra.py kuvat

# Kirjan kaaviot tuotetaan esimerkkien testatuista tulosteista ja datasta.
testaa: tarkista-kaaviot
.PHONY: tarkista-kaaviot
tarkista-kaaviot:
	@python3 kaaviot/tee.py --tarkista
