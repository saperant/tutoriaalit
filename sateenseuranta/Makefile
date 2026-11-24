# Säteenseuranta ja fysikaalinen valaistus. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := sateenseuranta
KIELI   := cpp
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvitus: esimerkkien PPM-kuvat PNG:iksi hakemistoon kuvat/.
# Ajetaan käsin, kun esimerkki muuttuu; PNG:t ovat versionhallinnassa.
CXX_KUVAT := $(shell command -v g++-14 || echo g++)
KUVAT     := 02-kamera 03-akne 05-whitted 08-polku 09-pbr 09-uuni 10-kohina

.PHONY: kuvat
kuvat:
	mkdir -p kuvat/tmp
	set -e; for k in $(KUVAT); do \
	    $(CXX_KUVAT) -std=c++23 -O2 -DKUVITUS esimerkit/$$k.cpp -o kuvat/tmp/$$k; \
	    (cd kuvat/tmp && ./$$k > /dev/null); \
	    python3 kuvat/ppm2png.py kuvat/tmp/$$k.ppm kuvat/$$k.png 3; \
	done
	rm -rf kuvat/tmp
