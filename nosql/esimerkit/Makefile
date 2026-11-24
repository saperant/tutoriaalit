# NoSQL-tietokannat: esimerkit.
#
#   make            tarkistukset ja kaikki esimerkit (pytest)
#   make ESIMERKKI=luku03   vain osa esimerkeistä (pytestin -k)
#   make siivoa     poistaa välimuistit
#
# Tietokannat käynnistyvät Docker-konteissa Testcontainersilla, joten
# Docker-palvelun on oltava käytettävissä. Kuvat haetaan oletuksena
# Docker Hubin virallisten kuvien Google-peilistä (ks. nosql/kontit.py).

SHELL := /bin/bash
export PYTHONPATH := $(CURDIR)
export PYTHONDONTWRITEBYTECODE := 1
# Etuliitemuuttuja lisäisi peilin myös Ryukin kuvaan ja johtaisi
# päättymättömään rekursioon; kuvat nimetään nosql/kontit.py:ssä.
unexport TESTCONTAINERS_HUB_IMAGE_NAME_PREFIX

ESIMERKKI ?=

.PHONY: kaikki tarkista siivoa

kaikki: tarkista
	timeout 900 python3 -m pytest testit $(if $(ESIMERKKI),-k '$(ESIMERKKI)')

tarkista:
	@python3 -c "import docker; docker.from_env().ping()" 2>/dev/null \
	    || { echo "Docker ei ole käytettävissä"; exit 1; }
	ruff check --no-cache --quiet .
	mypy --no-error-summary --cache-dir=/dev/null nosql testit \
	    luku*/*.py

siivoa:
	rm -rf .ruff_cache .mypy_cache .pytest_cache nosql/__pycache__ \
	    testit/__pycache__ luku*/__pycache__
