# DSP-algoritmien laitteistototeutus. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := dsp-laitteisto
KIELI   := projekti
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat tuotetaan skriptillä kuvat/piirra.py samoilla malleilla ja
# analyyseillä kuin testit; kuvat commitoidaan.
.PHONY: kuvat
kuvat:
	PYTHONDONTWRITEBYTECODE=1 python3 kuvat/piirra.py kuvat
