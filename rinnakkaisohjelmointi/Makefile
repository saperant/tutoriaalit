# Rinnakkaisohjelmointi. Kohteet: ks. ../yhteiset/paketti.mk.
# ThreadSanitizerin raportit tarkistetaan esimerkit/Makefilessä.
NIMI    := rinnakkaisohjelmointi
KIELI   := cpp
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat tuotetaan skriptillä kuvat/piirra.py; kuvat ovat versionhallinnassa.
.PHONY: kuvat
kuvat:
	python3 kuvat/piirra.py kuvat
