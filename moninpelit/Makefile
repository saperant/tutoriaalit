# Reaaliaikaiset moninpelit. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := moninpelit
KIELI   := cpp
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat tuotetaan skriptillä kuvat/piirra.py esimerkkien lokeista; kuvat
# commitoidaan.
.PHONY: kuvat
kuvat:
	PYTHONDONTWRITEBYTECODE=1 python3 kuvat/piirra.py kuvat
