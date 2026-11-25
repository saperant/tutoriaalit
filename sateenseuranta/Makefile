# Säteenseuranta ja fysikaalinen valaistus. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := sateenseuranta
KIELI   := cpp
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvitus: esimerkkien PPM-kuvat PNG:iksi hakemistoon kuvat/.
# Ajetaan käsin, kun esimerkki muuttuu; PNG:t ovat versionhallinnassa.
CXX_KUVAT := $(shell command -v g++-14 || echo g++)
# Muoto nimi:suurennos. Selittävät piirrokset ja mittaustulosten
# kuvaajat tekee kuvat/piirra.py (Matplotlib) esimerkkien
# .odotettu-tiedostoista.
KUVAT     := 02-kamera:1 03-akne:3 04-bvh:2 05-whitted:1 08-polku:3 \
             09-pbr:3 09-uuni:3 10-kohina:3 10-savykuvaus:2

.PHONY: kuvat
kuvat:
	mkdir -p kuvat/tmp
	set -e; for m in $(KUVAT); do \
	    k=$${m%%:*}; \
	    $(CXX_KUVAT) -std=c++23 -O2 -DKUVITUS esimerkit/$$k.cpp -o kuvat/tmp/$$k; \
	    (cd kuvat/tmp && ./$$k > /dev/null); \
	    python3 kuvat/ppm2png.py kuvat/tmp/$$k.ppm kuvat/$$k.png $${m#*:}; \
	done
	python3 kuvat/piirra.py
	rm -rf kuvat/tmp
