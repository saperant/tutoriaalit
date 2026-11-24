# Skaalautuvien järjestelmien suunnittelu: esimerkit.
#
#   make            tarkistukset ja kaikki esimerkit
#   make tarkista   ruff, mypy, pytest sekä YAML-, Compose-, Dockerfile-
#                   ja HAProxy-asetusten tarkistukset
#   make luku04/haproxy_vika   yksi esimerkki: ajetaan ja tulostetta
#                   verrataan tiedostoon luku04/haproxy_vika.odotettu
#   make siivoa     poistaa välimuistit
#
# Esimerkit käynnistävät Redisin, PostgreSQLin ja HAProxyn tavallisina
# prosesseina omiin väliaikaishakemistoihinsa ja vapaisiin portteihin,
# joten ne voi ajaa rinnakkain (make -j). Tarvitaan redis-server,
# haproxy, postgresql-16 ja Python-paketti psycopg.

SHELL := /bin/bash
export PYTHONPATH := $(CURDIR)
export PYTHONDONTWRITEBYTECODE := 1

ESIMERKIT := $(basename $(sort $(wildcard luku*/*.odotettu)))

.PHONY: kaikki tarkista siivoa $(ESIMERKIT)

kaikki: tarkista $(ESIMERKIT)

$(ESIMERKIT):
	@diff -u $@.odotettu <(timeout 180 python3 $@.py 2>&1) \
	    && echo "OK: $@"

tarkista:
	@for ohjelma in redis-server haproxy; do \
	    command -v $$ohjelma >/dev/null \
	        || { echo "puuttuu: $$ohjelma"; exit 1; }; \
	done
	@ls /usr/lib/postgresql/*/bin/initdb >/dev/null 2>&1 \
	    || { echo "puuttuu: PostgreSQL (postgresql-16)"; exit 1; }
	ruff check --no-cache --quiet .
	mypy --no-error-summary --cache-dir=/dev/null jarjestelma testit \
	    luku*/*.py
	python3 -m pytest testit
	yamllint -s .yamllint.yaml luku11/halytykset.yaml luku12/compose.yaml
	check-jsonschema -q --builtin-schema vendor.compose-spec \
	    luku12/compose.yaml
	hadolint --no-color luku12/Dockerfile
	HALLINTA=/tmp/x HAPROXY_PORTTI=1 A_PORTTI=2 B_PORTTI=3 C_PORTTI=4 \
	    haproxy -c -q -f luku04/haproxy.cfg
	HALLINTA=/tmp/x SISAAN=127.0.0.1:1 A_OSOITE=127.0.0.1:2 \
	    B_OSOITE=127.0.0.1:3 haproxy -c -q -f luku12/haproxy.cfg
	@echo "OK: tarkistukset"

siivoa:
	rm -rf .ruff_cache .mypy_cache .pytest_cache \
	    jarjestelma/__pycache__ testit/__pycache__ luku*/__pycache__
