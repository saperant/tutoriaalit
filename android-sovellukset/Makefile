# Android-sovellukset. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := android-sovellukset
KIELI   := projekti
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat: testit tallentavat kuvakaappaukset (KuvakaappausTest), ja
# kuvat/piirra.py kokoaa niistä tutoriaalin kuvat. Ajetaan käsin, ja
# kuvat commitoidaan.
.PHONY: kuvat
kuvat:
	$(MAKE) -C esimerkit testit
	python3 kuvat/piirra.py
