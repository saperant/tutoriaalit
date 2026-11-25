# Renderöinnin perusteet. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := renderoinnin-perusteet
KIELI   := cpp
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvitus: esimerkkien PPM-kuvat PNG:iksi hakemistoon kuvat/.
# Ajetaan käsin, kun esimerkki muuttuu; PNG:t ovat versionhallinnassa.
CXX_KUVAT := $(shell command -v g++-14 || echo g++)
# Muoto nimi:suurennos[:ruudukko]. -DKUVITUS kytkee esimerkeissä päälle
# kuvan kirjoittamisen (ja koko putken kohtauksessa suuremman koon);
# testattu tuloste ei riipu siitä. Selittävät piirrokset ja kuvaajat
# tekee kuvat/piirra.py (Matplotlib).
KUVAT     := 02-gamma:3 03-viivat:8:ruudukko 04-barysentrinen:3 \
             04-peitto:8:ruudukko 05-muunnokset:5 06-perspektiivi:3 \
             07-leikkaus:1 08-syvyys:1 09-varjostus:3 10-mipmap:3 \
             11-antialiasointi:8 12-putki:1

.PHONY: kuvat
kuvat:
	mkdir -p kuvat/tmp
	set -e; for m in $(KUVAT); do \
	    k=$${m%%:*}; loput=$${m#*:}; \
	    if [ -d esimerkit/$$k ]; then l=esimerkit/$$k/*.cpp; \
	    else l=esimerkit/$$k.cpp; fi; \
	    $(CXX_KUVAT) -std=c++23 -O2 -DKUVITUS $$l -o kuvat/tmp/$$k; \
	    (cd kuvat/tmp && ./$$k > /dev/null); \
	    python3 kuvat/ppm2png.py kuvat/tmp/$$k.ppm kuvat/$$k.png \
	        $$(echo $$loput | tr ':' ' '); \
	done
	python3 kuvat/piirra.py
	rm -rf kuvat/tmp
