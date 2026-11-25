# Testivetoinen kehitys ja testisuunnittelu. Kohteet: ks.
# ../yhteiset/paketti.mk.
NIMI    := testivetoinen-kehitys
KIELI   := projekti
RAKENNE := taito
include ../yhteiset/paketti.mk

# Luvun 5 kuva lasketaan esimerkin generaattorilla; kuva commitoidaan.
.PHONY: kuvat
kuvat:
	PYTHONDONTWRITEBYTECODE=1 python3 kuvat/piirra.py
