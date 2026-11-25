# Pelifysiikka. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := pelifysiikka
KIELI   := cpp
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvitus (ajetaan käsin, kuvat commitoidaan): kuvat/piirra.py kääntää
# esimerkit, ajaa ne kuvitustilassa ja kokoaa niiden tallentamat kuvat
# ja aikasarjat PNG-kuviksi.
.PHONY: kuvat
kuvat:
	PYTHONDONTWRITEBYTECODE=1 python3 kuvat/piirra.py

# Luvun 13 koe: vertailuajon tiiviste molemmilla kääntäjillä, ensin
# liukulukujen yhdistämiskielto päällä (-O0 ja -O2), sitten ilman.
# -mfma antaa kääntäjälle luvan FMA-käskyihin x86-64:llä; ARM:lla ne
# ovat aina käytettävissä.
FMA := $(if $(filter x86_64,$(shell uname -m)),-mfma)
.PHONY: tiivisteet
tiivisteet:
	@for cxx in g++-14 clang++-20; do \
	  for liput in "-O0" "-O2 $(FMA)" "-O2 $(FMA) -DSALLI_FMA"; do \
	    $$cxx -std=c++23 $$liput esimerkit/13-determinismi.cpp \
	      -o /tmp/pelifysiikka-tiiviste && \
	    printf '%-10s %-22s ' "$$cxx" "$$liput" && \
	    /tmp/pelifysiikka-tiiviste tiiviste | tail -1; \
	  done; \
	done; rm -f /tmp/pelifysiikka-tiiviste
