# GPU-laskenta. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := gpu-laskenta
KIELI   := projekti
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvitus: algoritmien periaatekuvat ja roofline-kuvaaja (Matplotlib).
# Ajetaan käsin; PNG:t ovat versionhallinnassa.
.PHONY: kuvat
kuvat:
	python3 kuvat/piirra.py
