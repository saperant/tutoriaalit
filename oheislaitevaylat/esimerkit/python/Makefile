# Python-mallit: tarkistukset (ruff, mypy --strict), yksikkötestit
# (pytest) ja esimerkkien tulosteiden vertailu tiedostoihin
# <nimi>.odotettu.

PYTHON    ?= python3
ESIMERKIT := avokollektori uart_kehys uart_nopeus spi_moodit \
             spi_laitteet i2c_kaavio i2c_virheet can_kehys \
             can_arbitraatio can_virheet can_ajoitus can_isotp
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: kaikki tarkista testit kaaviot siivoa $(ESIMERKIT)

kaikki: tarkista testit kaaviot $(ESIMERKIT)

# Kirjan ajoituskaaviot (../kaaviot/*.json) tuotetaan malleista;
# muutos mallissa paljastuu tässä. Päivitys: aaltokaaviot.py kirjoita.
kaaviot:
	$(PYTHON) aaltokaaviot.py tarkista ../kaaviot

tarkista:
	ruff check --no-cache --quiet .
	mypy --no-incremental --cache-dir=/dev/null . > /dev/null

testit:
	$(PYTHON) -m pytest -q > /dev/null

$(ESIMERKIT):
	@tulos=$$($(PYTHON) $@.py) || { echo "VIRHE: $@ kaatui"; exit 1; }; \
	printf '%s\n' "$$tulos" | diff -u $@.odotettu - \
	    || { echo "VIRHE: $@ poikkeaa odotetusta"; exit 1; }

siivoa:
	rm -rf __pycache__ mallit/__pycache__ testit/__pycache__ \
	    .mypy_cache .ruff_cache
