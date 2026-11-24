# Esimerkit, joita yhteinen testaaja ei aja:
#
#   make           pytest-testit hakemistoesimerkeissä ja luvun 3
#                  pakettiesimerkin tarkistukset (ruff, mypy, pytest)
#   make siivoa    poistaa välimuistit
#
# Yksittäinen esimerkki ajetaan suoraan, esim.
#   python3 04-loki.py < 04-loki.syote

TESTIT := $(sort $(patsubst %/,%,$(dir $(wildcard */test_*.py))))
export PYTHONDONTWRITEBYTECODE := 1
PYTEST := python3 -m pytest -q -p no:cacheprovider

.PHONY: kaikki paketti siivoa $(TESTIT)

kaikki: $(TESTIT) paketti

$(TESTIT):
	cd $@ && $(PYTEST)

# Luvun 3 paketti testataan kehityshakemistosta asentamatta sitä.
paketti:
	cd 03-paketti && ruff check --no-cache --quiet . \
	    && MYPYPATH=src mypy --strict --no-error-summary \
	           --cache-dir=/dev/null src tests \
	    && PYTHONPATH=src $(PYTEST) tests \
	    && PYTHONPATH=src python3 -m lokikoonti --version

siivoa:
	find . -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache \
	    | xargs rm -rf
