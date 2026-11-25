# Suorituskyvyn analyysi ja optimointi. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := suorituskyky
KIELI   := c
RAKENNE := taito
include ../yhteiset/paketti.mk

# Luvun 4 kutsupuu tuotetaan Callgrindin tallennetusta tulosteesta.
testaa: tarkista-kaaviot
.PHONY: tarkista-kaaviot kuvat
tarkista-kaaviot:
	@python3 kaaviot/tee.py --tarkista

# Kuvaajat piirretään tiedostoista esimerkit/tulokset/; kuvat commitoidaan.
kuvat:
	python3 kuvat/piirra.py kuvat
