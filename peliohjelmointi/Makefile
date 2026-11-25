# Peliohjelmointi. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := peliohjelmointi
KIELI   := cpp
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvitus (ajetaan käsin, kuvat commitoidaan): Kipinän lopputila
# PNG-kuvaksi ja muut kuvat esimerkkien tulosteista (kuvat/piirra.py).
.PHONY: kuvat
kuvat:
	mkdir -p kuvat/tmp
	$(shell command -v g++-14 || echo g++) -std=c++23 -O2 \
	    esimerkit/12-kipina/*.cpp -o kuvat/tmp/kipina
	cd kuvat/tmp && ./kipina < ../../esimerkit/12-kipina.syote > /dev/null
	python3 kuvat/ppm2png.py kuvat/tmp/kipina.ppm kuvat/kipina.png 3
	rm -rf kuvat/tmp
	PYTHONDONTWRITEBYTECODE=1 python3 kuvat/piirra.py kuvat
