# Laitteiston verifiointi. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := verifiointi
KIELI   := projekti
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat tuotetaan skriptillä kuvat/piirra.py (Matplotlib, Icarus Verilog
# ja cocotb); kuvat commitoidaan.
.PHONY: kuvat
kuvat:
	python3 kuvat/piirra.py
