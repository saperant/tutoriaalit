# Ohjelmoinnin perusteiden esimerkit.
#
#   make           ajaa hakemistoesimerkkien pytest-testit
#   make siivoa    poistaa pytestin ja Pythonin välimuistit
#
# Yksittäinen esimerkki ajetaan suoraan:  python3 02-aika.py
# Syötteen voi antaa tiedostosta:         python3 02-lampotila.py < 02-lampotila.syote

TESTIT := $(sort $(patsubst %/,%,$(dir $(wildcard */test_*.py))))
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: kaikki siivoa $(TESTIT)

kaikki: $(TESTIT)

$(TESTIT):
	cd $@ && python3 -m pytest -q -p no:cacheprovider

siivoa:
	rm -rf */__pycache__ */.pytest_cache
