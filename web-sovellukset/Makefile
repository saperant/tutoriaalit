# Web-sovellukset. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := web-sovellukset
KIELI   := projekti
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvitus: kuvakaappaukset valmiista sovelluksesta (Playwright,
# esimerkit/kuvitus) ja aikajanakuvat (Matplotlib, kuvat/piirra.py).
# Ajetaan käsin, ja kuvat commitoidaan.
.PHONY: kuvat
kuvat:
	$(MAKE) -C esimerkit kuvat
	python3 kuvat/piirra.py
