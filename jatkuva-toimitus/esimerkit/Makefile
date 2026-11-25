# Jatkuva integraatio ja toimitus: esimerkit.
#
#   make              tarkistukset, testit ja lukujen esimerkit
#   make tarkista     ruff, mypy sekä työnkulun YAML- ja skeematarkistus
#   make pytest       putken osien ja esimerkkisovelluksen testit
#   make luku08/strategiat   yksi esimerkki: ajetaan ja tulostetta
#                     verrataan tiedostoon luku08/strategiat.odotettu
#   make paivita      kirjoittaa odotetut tulosteet uudelleen
#
# Esimerkit käyttävät Pythonin standardikirjastoa ja Gitiä. Väliaikaiset
# repositoriot ja paketit tehdään väliaikaishakemistoihin, joten ajo ei
# jätä jälkiä.

SHELL := /bin/bash
export PYTHONPATH := $(CURDIR)
export PYTHONDONTWRITEBYTECODE := 1

ESIMERKIT := $(basename $(sort $(wildcard luku*/*.py)))

.PHONY: kaikki tarkista pytest paivita siivoa $(ESIMERKIT)

kaikki: tarkista pytest $(ESIMERKIT)

tarkista:
	ruff check --no-cache --quiet .
	mypy --no-error-summary --cache-dir=/dev/null toimitus testit luku*
	yamllint -d relaxed luku06/tyonkulku.yml
	check-jsonschema -q --builtin-schema vendor.github-workflows \
	    luku06/tyonkulku.yml
	@echo "OK: tarkistukset"

pytest:
	@python3 -m pytest testit > /dev/null || python3 -m pytest testit
	@cd sovellus && { python3 -m pytest > /dev/null || python3 -m pytest; }
	@echo "OK: testit"

$(ESIMERKIT):
	@diff -u $@.odotettu <(timeout 300 python3 $@.py) && echo "OK: $@"

paivita:
	@for e in $(ESIMERKIT); do python3 $$e.py > $$e.odotettu; done

siivoa:
	@true
