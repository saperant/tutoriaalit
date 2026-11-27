# Esimerkit, joita yhteinen testaaja ei aja:
#
#   make           pytest-testit (fm/, paketti/), vertailu Clangilla ja
#                  GNU Radio -lohkokaavio (gnuradio/)
#   make gnuradio  vain GNU Radio -osa; GNURADIO=ohita jattaa sen pois
#   make mittaa    C++-ketjun lapaisy (tulosta ei verrata)
#   make siivoa    poistaa valimuistit ja kaannokset
#
# Yksittainen testi ajetaan esimerkiksi nain:
#   cd fm && python3 -m pytest -q -k rds

TESTIT := $(sort $(patsubst %/,%,$(dir $(wildcard */test_*.py))))
export PYTHONDONTWRITEBYTECODE := 1
PYTEST := python3 -m pytest -q -p no:cacheprovider
TYO := $(CURDIR)/build

.PHONY: kaikki clang gnuradio mittaa siivoa $(TESTIT)

kaikki: $(TESTIT) clang gnuradio

$(TESTIT):
	cd $@ && $(PYTEST)

# @alku clang
# Sama vertailu toisella kaantajalla: tulosteen on oltava sama.
clang:
	mkdir -p $(TYO)/clang
	cd $(TYO)/clang && CXX=clang++-20 python3 $(CURDIR)/vertailu/main.py \
	    | diff - $(CURDIR)/vertailu.odotettu
# @loppu clang

# @alku gnuradio
# GNU Radio -ohjelmat ajetaan jakelun Pythonilla (gnuradio/gr-python),
# vertailun lahtotiedot ja itse vertailu tavallisella python3:lla.
# GNU Radio tulostaa omia ilmoituksiaan vakiotulosteeseen, joten sen
# tuloste menee lokiin ja verrattavat luvut luetaan tiedostoista.
GR := $(CURDIR)/gnuradio
gnuradio:
ifeq ($(GNURADIO),ohita)
	@echo "OHITETTU: GNU Radio -esimerkit (GNURADIO=ohita)"
else
	@$(GR)/gr-python --tarkista > /dev/null
	@ruff check -q $(GR)
	@mkdir -p $(TYO)/gnuradio
	@cd $(TYO)/gnuradio && python3 $(GR)/oma/valmistele.py
	@cd $(TYO)/gnuradio && { \
	    $(GR)/gr-python $(GR)/lohkokaavio/test_tehomittari.py \
	    && $(GR)/gr-python $(GR)/lohkokaavio/fm_mono.py \
	        asema.cu8 gr.f32 taso.f32; } > loki.txt 2>&1 \
	    || { cat loki.txt; exit 1; }
	@cd $(TYO)/gnuradio && python3 $(GR)/oma/vertaa.py \
	    | diff - $(GR)/vertailu.odotettu
	@echo "OK: GNU Radio -lohkokaavio ja oma lohko"
endif
# @loppu gnuradio

mittaa:
	mkdir -p $(TYO)
	g++-14 -std=c++23 -O2 -o $(TYO)/ketju 08-reaaliaika/*.cpp
	$(TYO)/ketju --mittaa

siivoa:
	rm -rf $(TYO)
	find . -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache \
	    | xargs rm -rf
