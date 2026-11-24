# Laitteiston kuvausstandardit: esimerkit.
#
#   make              tarkistaa Pythonin (ruff, mypy --strict), ajaa
#                     yksikkötestit ja esimerkit ja vertaa tulosteita
#                     tiedostoihin *.odotettu
#   make 05-regblock  ajaa yhden esimerkin
#   make tuota        tuottaa hakemiston tuotettu/ kuvauksista
#   make paivita      kirjoittaa odotetut tulosteet uudelleen (vain kun
#                     muutos on tarkistettu käsin)
#
# Esimerkit ajavat työkalut väliaikaisissa hakemistoissa, joten ne voi
# ajaa rinnakkain (-j). Verilatorin sisäinen Make ei peri ulomman Maken
# MAKEFLAGS-muuttujaa (kuvaus/ajo.py).

PYTHON    ?= python3
ESIMERKIT := $(basename $(wildcard [0-9][0-9]-*.py))
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: kaikki tarkista testit tuota paivita siivoa $(ESIMERKIT)

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

tuota:
	@$(PYTHON) 11-tahdissa.py --kirjoita

paivita:
	@for e in $(ESIMERKIT); do $(PYTHON) $$e.py > $$e.odotettu || exit 1; done

siivoa:
	@rm -rf __pycache__ kuvaus/__pycache__ testit/__pycache__ \
	    .mypy_cache .ruff_cache .pytest_cache
