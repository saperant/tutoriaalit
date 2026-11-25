# Lukujen esitys ja kiinteän pilkun aritmetiikka.
# Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := kiintea-pilkku
KIELI   := c python systemverilog
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat tuotetaan skriptillä kuvat/piirra.py esimerkkien funktioilla;
# kuvat commitoidaan.
.PHONY: kuvat
kuvat:
	PYTHONDONTWRITEBYTECODE=1 python3 kuvat/piirra.py kuvat
