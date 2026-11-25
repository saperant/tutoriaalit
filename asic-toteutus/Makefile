# ASIC-toteutus. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := asic-toteutus
KIELI   := python systemverilog
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat tuotetaan esimerkkien funktioista ja testatuista tulosteista
# skriptillä kuvat/piirra.py (tarvitsee Matplotlibin ja Yosysin);
# PNG-tiedostot commitoidaan.
.PHONY: kuvat
kuvat:
	python3 kuvat/piirra.py kuvat
