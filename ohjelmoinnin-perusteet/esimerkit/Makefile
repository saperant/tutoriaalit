# Ohjelmoinnin perusteiden esimerkit.
#
#   make           ajaa hakemistoesimerkkien pytest-testit ja tarkistaa
#                  tehtävien pohjat ja malliratkaisut
#   make siivoa    poistaa pytestin ja Pythonin välimuistit
#
# Yksittäinen esimerkki ajetaan suoraan:  python3 02-aika.py
# Syötteen voi antaa tiedostosta:         python3 02-lampotila.py < 02-lampotila.syote
# Kokeile itse -tehtävät:                 python3 tarkista.py --lista

TESTIT := $(sort $(patsubst %/,%,$(dir $(wildcard */test_*.py))))
MYPY   := mypy --config-file ../pyproject.toml --no-error-summary \
          --cache-dir=/dev/null
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: kaikki siivoa tarkista-tehtavat $(TESTIT)

kaikki: $(TESTIT) tarkista-tehtavat

$(TESTIT):
	cd $@ && python3 -m pytest -q -p no:cacheprovider

# Tehtävien pohjat ja malliratkaisut ovat alihakemistoissa, joita
# tutoriaalin yhteinen testaaja ei käy läpi. Tässä ne tarkistetaan
# ruffilla ja mypyllä, malliratkaisut ajetaan tehtävien testejä vasten
# ja varmistetaan, ettei yksikään pohja kelpaa ratkaisuksi sellaisenaan.
tarkista-tehtavat:
	ruff check --no-cache --quiet tarkista.py tehtavat
	MYPYPATH=tehtavat/tuki $(MYPY) tehtavat/pohjat/*.py
	MYPYPATH=tehtavat/tuki $(MYPY) tehtavat/ratkaisut/*.py
	$(MYPY) tehtavat/tuki/*.py
	for h in tehtavat/tuki/*/; do $(MYPY) $$h*.py || exit 1; done
	python3 tarkista.py --ratkaisut
	python3 tarkista.py --pohjat

siivoa:
	rm -rf */__pycache__ */.pytest_cache tehtavat/*/__pycache__ \
	    tehtavat/*/.pytest_cache
