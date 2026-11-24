# Esimerkit, joita yhteinen testaaja ei aja:
#
#   make           pytest-testit hakemistoesimerkeissä (test_*.py)
#   make siivoa    poistaa välimuistit
#
# Yksittäinen testi ajetaan esimerkiksi näin:
#   cd 11-linkki && python3 -m pytest -q -k crc

TESTIT := $(sort $(patsubst %/,%,$(dir $(wildcard */test_*.py))))
export PYTHONDONTWRITEBYTECODE := 1
PYTEST := python3 -m pytest -q -p no:cacheprovider

.PHONY: kaikki siivoa $(TESTIT)

kaikki: $(TESTIT)

$(TESTIT):
	cd $@ && $(PYTEST)

siivoa:
	find . -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache \
	    | xargs rm -rf
