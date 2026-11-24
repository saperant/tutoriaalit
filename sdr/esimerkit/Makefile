# Esimerkit, joita yhteinen testaaja ei aja:
#
#   make           pytest-testit (fm/, paketti/) ja vertailu Clangilla
#   make mittaa    C++-ketjun lapaisy (tulosta ei verrata)
#   make siivoa    poistaa valimuistit ja kaannokset
#
# Yksittainen testi ajetaan esimerkiksi nain:
#   cd fm && python3 -m pytest -q -k rds

TESTIT := $(sort $(patsubst %/,%,$(dir $(wildcard */test_*.py))))
export PYTHONDONTWRITEBYTECODE := 1
PYTEST := python3 -m pytest -q -p no:cacheprovider
TYO := $(CURDIR)/build

.PHONY: kaikki clang mittaa siivoa $(TESTIT)

kaikki: $(TESTIT) clang

$(TESTIT):
	cd $@ && $(PYTEST)

# @alku clang
# Sama vertailu toisella kaantajalla: tulosteen on oltava sama.
clang:
	mkdir -p $(TYO)/clang
	cd $(TYO)/clang && CXX=clang++-20 python3 $(CURDIR)/vertailu/main.py \
	    | diff - $(CURDIR)/vertailu.odotettu
# @loppu clang

mittaa:
	mkdir -p $(TYO)
	g++-14 -std=c++23 -O2 -o $(TYO)/ketju 08-reaaliaika/*.cpp
	$(TYO)/ketju --mittaa

siivoa:
	rm -rf $(TYO)
	find . -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache \
	    | xargs rm -rf
