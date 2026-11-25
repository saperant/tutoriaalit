# Tietorakenteet. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := tietorakenteet
KIELI   := c
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kirjan kaaviot tuotetaan esimerkkien testatuista tulosteista.
testaa: tarkista-kaaviot
.PHONY: tarkista-kaaviot
tarkista-kaaviot:
	@python3 kaaviot/tee.py --tarkista

# Kuvaajat tuotetaan skriptillä kuvat/piirra.py; kuvat commitoidaan.
.PHONY: kuvat
kuvat:
	python3 kuvat/piirra.py kuvat
