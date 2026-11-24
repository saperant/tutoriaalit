# Renderöinnin perusteet. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := renderoinnin-perusteet
KIELI   := cpp
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvitus: esimerkkien PPM-kuvat PNG:iksi hakemistoon kuvat/.
# Ajetaan käsin, kun esimerkki muuttuu; PNG:t ovat versionhallinnassa.
CXX_KUVAT := $(shell command -v g++-14 || echo g++)
KUVAT     := 02-gamma 04-barysentrinen 06-perspektiivi 09-varjostus \
             10-mipmap 12-putki

.PHONY: kuvat
kuvat:
	mkdir -p kuvat/tmp
	set -e; for k in $(KUVAT); do \
	    if [ -d esimerkit/$$k ]; then l=esimerkit/$$k/*.cpp; \
	    else l=esimerkit/$$k.cpp; fi; \
	    $(CXX_KUVAT) -std=c++23 -O2 $$l -o kuvat/tmp/$$k; \
	    (cd kuvat/tmp && ./$$k > /dev/null); \
	    python3 kuvat/ppm2png.py kuvat/tmp/$$k.ppm kuvat/$$k.png 3; \
	done
	rm -rf kuvat/tmp
