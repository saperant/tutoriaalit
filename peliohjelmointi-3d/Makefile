# 3D-peliohjelmointi. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := peliohjelmointi-3d
KIELI   := cpp
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvitus (ajetaan käsin, kuvat commitoidaan): kuvat/piirra.py kääntää
# esimerkit, ajaa ne kuvitustilassa ja kokoaa niiden tallentamat kuvat
# ja reittitiedostot PNG-kuviksi.
.PHONY: kuvat
kuvat:
	PYTHONDONTWRITEBYTECODE=1 python3 kuvat/piirra.py
