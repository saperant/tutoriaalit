# Analogiaelektroniikka. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := analogiaelektroniikka
KIELI   := python
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat (piirikaaviot schemdrawilla ja kuvaajat ngspicen tuloksista)
# tuotetaan skriptillä kuvat/piirra.py; kuvat commitoidaan.
.PHONY: kuvat
kuvat:
	python3 kuvat/piirra.py kuvat
