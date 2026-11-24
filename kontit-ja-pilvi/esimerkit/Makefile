# Kontit ja pilvi: esimerkit.
#
#   make               kaikki alla olevat
#   make staattiset    tarkistimet, yksikkötestit ja odotetut tulosteet
#                      (ei tarvitse Dockeria)
#   make docker        rakentaa kuvat ja ajaa ne: testit-vaihe,
#                      Compose-sovellus ja Helm-kaavion renderöinti
#   make nimiavaruudet kontti ilman konttiajoympäristöä (unshare)
#   make siivoa        poistaa välimuistit
#
# docker ja nimiavaruudet ohitetaan ilmoituksella, jos ympäristössä ei
# ole Dockeria tai oikeuksia nimiavaruuksien luontiin (esim. kehitys-
# kontin sisällä). Silloin vain staattiset tarkistukset ajetaan.

SHELL := /bin/bash

.PHONY: kaikki staattiset docker nimiavaruudet siivoa

kaikki: staattiset docker nimiavaruudet

staattiset:
	testit/staattiset.sh

docker:
	@if docker info >/dev/null 2>&1; then \
	    diff -u testit/docker.odotettu <(testit/docker.sh) \
	        && echo "OK: testit/docker.odotettu"; \
	else \
	    echo "Docker ei käytettävissä: kuvien rakennus ja ajo ohitetaan"; \
	fi

nimiavaruudet:
	@if unshare --pid --fork true 2>/dev/null \
	        || sudo -n unshare --pid --fork true 2>/dev/null; then \
	    diff -u nimiavaruudet.odotettu <(./nimiavaruudet.sh) \
	        && echo "OK: nimiavaruudet.odotettu"; \
	else \
	    echo "Ei oikeuksia nimiavaruuksiin: unshare-esimerkki ohitetaan"; \
	fi

siivoa:
	rm -rf .mypy_cache .ruff_cache sovellus/__pycache__ __pycache__ \
	    iac/__pycache__
