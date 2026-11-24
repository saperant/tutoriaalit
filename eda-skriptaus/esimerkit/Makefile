# EDA-työkaluketjujen automatisointi: esimerkit.
#
#   make              tarkistaa Pythonin (ruff, mypy --strict), ajaa
#                     yksikkötestit ja esimerkit ja vertaa tulosteita
#                     tiedostoihin *.odotettu
#   make 07-regressio ajaa yhden esimerkin
#   make paivita      kirjoittaa odotetut tulosteet uudelleen (vain kun
#                     muutos on tarkistettu käsin)
#
# Esimerkit ajavat työkalut tilapäishakemistoissa, joten ne voi ajaa
# rinnakkain (-j). Ulomman Maken MAKEFLAGS poistetaan työkalujen omista
# Make-kutsuista (vuo/ajo.py ja 02-make.py).

PYTHON    ?= python3
ESIMERKIT := $(basename $(wildcard [0-9][0-9]-*.py))
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: kaikki tarkista testit paivita siivoa $(ESIMERKIT)

kaikki: tarkista testit $(ESIMERKIT)

tarkista:
	@ruff check --no-cache .
	@mypy --no-incremental --cache-dir=/dev/null .

testit:
	@$(PYTHON) -m pytest -q

$(ESIMERKIT):
	@tulos=$$($(PYTHON) $@.py) || { echo "VIRHE: $@ kaatui"; exit 1; }; \
	printf '%s\n' "$$tulos" | diff -u $@.odotettu - \
	    || { echo "VIRHE: $@ poikkeaa odotetusta"; exit 1; }; \
	echo "OK: $@"

paivita:
	@for e in $(ESIMERKIT); do $(PYTHON) $$e.py > $$e.odotettu || exit 1; done

siivoa:
	@rm -rf __pycache__ vuo/__pycache__ testit/__pycache__ .mypy_cache \
	    .ruff_cache
