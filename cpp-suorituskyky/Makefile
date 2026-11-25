# C++:n suorituskyky. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := cpp-suorituskyky
KIELI   := cpp
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvaajat piirretään tulostiedostoista (esimerkit/tulokset/); PNG:t
# commitoidaan.
.PHONY: kuvat
kuvat:
	python3 kuvat/piirra.py kuvat
