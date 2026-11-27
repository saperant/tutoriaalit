# Korkean tason mallinnus (SystemC/TLM). Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := hlm-mallinnus
KIELI   := projekti
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvat tuotetaan skriptillä kuvat/piirra.py esimerkin 11-kvantti
# jäljestä ja esimerkin 15-keskeytykset testatusta tulosteesta; kuvat
# commitoidaan.
.PHONY: kuvat
kuvat:
	esimerkit/testaa.sh 11-kvantti
	PYTHONDONTWRITEBYTECODE=1 python3 kuvat/piirra.py kuvat \
	    esimerkit/build/11-kvantti/ohjelma
