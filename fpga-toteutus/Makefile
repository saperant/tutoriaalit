# FPGA-toteutus. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := fpga-toteutus
KIELI   := systemverilog
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat tuotetaan työkalujen raporteista ja simuloidun kortin ajosta
# skriptillä kuvat/piirra.py; PNG-tiedostot commitoidaan.
.PHONY: kuvat
kuvat:
	$(MAKE) -C esimerkit -s -j4 kuvadata
	python3 kuvat/piirra.py esimerkit/rakennus kuvat
	$(MAKE) -C esimerkit -s siivoa
