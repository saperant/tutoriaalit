# Integraatiotestaus ja Testcontainers: esimerkit.
#
#   make              tarkistukset, testit ja lukujen esimerkit
#   make tarkista     ruff, mypy sekä CI-esimerkin YAML- ja skeematarkistus
#   make pytest       testit/ (yksikkö-, sopimus- ja integraatiotestit)
#   make luku02/murre yksi esimerkki: ajetaan ja tulostetta verrataan
#                     tiedostoon luku02/murre.odotettu
#   make siivoa       poistaa välimuistit ja apukuvan
#
# Testit ja esimerkit käynnistävät kontteja Dockeriin, joten Dockerin
# on oltava käytettävissä (kehityskontissa isännän Docker-soketti).
# Kuvat haetaan Docker Hubin Google-peilistä; peilin voi vaihtaa
# muuttujalla TESTIKUVAT_PEILI (ks. testiapu/kuvat.py).

SHELL := /bin/bash
export PYTHONPATH := $(CURDIR)
export PYTHONDONTWRITEBYTECODE := 1

ESIMERKIT := $(filter-out luku04/laajuudet,\
    $(basename $(sort $(wildcard luku*/*.odotettu))))

.PHONY: kaikki tarkista docker pytest luku04/laajuudet siivoa $(ESIMERKIT)

kaikki: tarkista pytest luku04/laajuudet $(ESIMERKIT)

docker:
	@python3 -c "import docker; docker.from_env().ping()" 2>/dev/null \
	    || { echo "Docker ei ole käytettävissä"; exit 1; }

tarkista:
	ruff check --no-cache --quiet .
	mypy --no-error-summary --cache-dir=/dev/null varasto testiapu \
	    testit apukuva luku0*
	yamllint -d relaxed luku10/integraatio.yml
	check-jsonschema -q --builtin-schema vendor.github-workflows \
	    luku10/integraatio.yml
	@echo "OK: tarkistukset"

pytest: docker
	@timeout 900 python3 -m pytest testit

# Fixturejen laajuudet: pytestin --setup-show-tuloste ilman
# fixture-luetteloita, jotta rivit mahtuvat sivulle.
luku04/laajuudet:
	@diff -u $@.odotettu <(python3 -m pytest -q --setup-show \
	    luku04/test_laajuudet.py \
	    | sed -e 's/ (fixtures used: [^)]*)//') && echo "OK: $@"

$(ESIMERKIT): docker
	@diff -u $@.odotettu <(timeout 300 python3 $@.py) && echo "OK: $@"

siivoa:
	rm -rf .ruff_cache .mypy_cache .pytest_cache
	find . -name __pycache__ -prune -exec rm -rf {} +
	-@docker rmi -f integraatiotestaus-apukuva:1 >/dev/null 2>&1
