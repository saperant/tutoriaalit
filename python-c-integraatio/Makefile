# Python ja C/C++ yhteen. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := python-c-integraatio
KIELI   := projekti
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kutsun hinnan mittaus ja kuvaaja (luku 9). Ajetaan käsin koneella,
# jossa ei ole muuta kuormaa; tulos ja kuva ovat versionhallinnassa.
.PHONY: kuvat
kuvat:
	$(MAKE) -C esimerkit 09-hinta
	python3 kuvat/piirra.py kuvat
