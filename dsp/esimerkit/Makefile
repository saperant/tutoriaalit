# Esimerkit, joita yhteinen testaaja ei aja:
#
#   make           pytest-testit, vertailu Clangilla ja generoitu otsake
#   make siivoa    poistaa valimuistit
#
# Yksittainen testi ajetaan esimerkiksi nain:
#   cd vertailu && python3 -m pytest -q -k fft

export PYTHONDONTWRITEBYTECODE := 1
PYTEST := python3 -m pytest -q -p no:cacheprovider

.PHONY: kaikki pytest clang otsake siivoa

kaikki: pytest clang otsake

# @alku kohteet
pytest:
	cd vertailu && $(PYTEST)

# Sama vertailu toisella kaantajalla: tulosteen on oltava sama.
clang:
	CC=clang-20 python3 vertailu/main.py | diff - vertailu.odotettu

# Versionhallinnassa oleva otsake vastaa generaattorin tulostetta.
otsake:
	python3 05-kertoimet.py | diff - 05-fir/kertoimet.h
# @loppu kohteet

siivoa:
	find . -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache \
	    | xargs rm -rf
