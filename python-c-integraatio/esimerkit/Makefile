# Esimerkkien käännös ja testit.
#
#   make           kääntää laajennukset hakemistoon build/, tarkistaa
#                  Python-koodin (ruff, mypy --strict), ajaa esimerkit ja
#                  vertaa tulosteet tiedostoihin main.odotettu sekä
#                  rakentaa ja testaa luvun 12 pyöräpaketin
#   make siivoa    poistaa käännöstuotteet
#
# Yksittäinen esimerkki ajetaan käännöksen jälkeen esimerkiksi:
#   cd 05-pybind11 && PYTHONPATH=../build python3 main.py

PYTHON := python3
export PIP_ROOT_USER_ACTION := ignore
export PIP_DISABLE_PIP_VERSION_CHECK := 1
CC     := $(shell command -v gcc-14 || command -v gcc)
CXX    := $(shell command -v g++-14 || command -v g++)
B      := build

# @alku liput
EXT    := $(shell $(PYTHON) -c \
            "import sysconfig as s; print(s.get_config_var('EXT_SUFFIX'))")
PYINC  := -isystem $(shell $(PYTHON) -c \
            "import sysconfig; print(sysconfig.get_path('include'))")
PB11   := -isystem $(shell $(PYTHON) -c \
            "import pybind11; print(pybind11.get_include())")
NB     := $(shell $(PYTHON) -c \
            "import nanobind; print(nanobind.source_dir() + '/..')")
NBINC  := -isystem $(NB)/include -isystem $(NB)/ext/robin_map/include
VAROITUKSET := -Wall -Wextra -Werror
CFLAGS   := -O2 -std=c17 -fPIC $(VAROITUKSET)
CXXFLAGS := -O2 -std=c++20 -fPIC -fvisibility=hidden $(VAROITUKSET)
# @loppu liput

KIRJASTOT := $(B)/libtarkistus.so $(B)/libsuodatin.so
PYBIND11  := mittari muunnos takaisin kuva rinnakkain hinta
NANOBIND  := tilasto_nb kuva_nb
MODUULIT  := $(KIRJASTOT) $(PYBIND11:%=$(B)/%$(EXT)) \
             $(NANOBIND:%=$(B)/%$(EXT)) $(B)/raaka$(EXT)
# Lähdetiedostot etsitään esimerkkihakemistoista.
vpath %.cpp $(wildcard [0-9]*)
ESIMERKIT := $(sort $(patsubst %/main.py,%,$(wildcard */main.py)))

.PHONY: kaikki tarkista $(ESIMERKIT) kaatuminen paketti siivoa

kaikki: tarkista $(ESIMERKIT) kaatuminen paketti

$(B):
	mkdir -p $@

# @alku saannot
$(B)/libtarkistus.so: 03-ctypes/tarkistus.c 03-ctypes/tarkistus.h | $(B)
	$(CC) $(CFLAGS) -shared $< -o $@ -lm

$(B)/libsuodatin.so: 04-c-rajapinta/suodatin.cpp \
                     04-c-rajapinta/suodatin.h | $(B)
	$(CXX) $(CXXFLAGS) -shared $< -o $@

$(B)/%$(EXT): %.cpp | $(B)
	$(CXX) $(CXXFLAGS) $(PB11) $(PYINC) -shared $< -o $@

# nanobindin oma ydin käännetään kerran (kolmannen osapuolen koodia,
# joten ilman -Werror:ia) ja linkitetään jokaiseen moduuliin.
$(B)/nanobind.o: | $(B)
	$(CXX) -O2 -std=c++20 -fPIC -fvisibility=hidden $(NBINC) $(PYINC) \
	    -c $(NB)/src/nb_combined.cpp -o $@

$(NANOBIND:%=$(B)/%$(EXT)): $(B)/%$(EXT): %.cpp $(B)/nanobind.o
	$(CXX) $(CXXFLAGS) $(NBINC) $(PYINC) -shared $^ -o $@

$(B)/raaka$(EXT): 11-c-api/raaka.c | $(B)
	$(CC) $(CFLAGS) $(PYINC) -shared $< -o $@
# @loppu saannot

tarkista:
	ruff check --no-cache --quiet .

# Jokainen esimerkki: tyyppitarkistus omien .pyi-tiedostojen kanssa,
# ajo ja tulosteen vertailu (virhevirta ohitetaan).
$(ESIMERKIT): $(MODUULIT)
	cd $@ && mypy --strict --no-error-summary --cache-dir=/dev/null main.py
	cd $@ && PYTHONPATH=../$(B) $(PYTHON) main.py 2>/dev/null \
	    | diff -u main.odotettu -

# @alku kaatuminen
# Kaatuva ohjelma: prosessin on päätyttävä signaaliin, ja faulthandlerin
# on näytettävä Python-pino. Polut ja säikeen tunniste karsitaan pois.
kaatuminen: | $(B)
	cd 11-c-api && mypy --strict --no-error-summary \
	    --cache-dir=/dev/null kaatuu.py
	cd 11-c-api && ! $(PYTHON) -X faulthandler kaatuu.py \
	    2> ../$(B)/kaatuu.txt
	grep -E '^Fatal Python error|^  File ' $(B)/kaatuu.txt \
	    | sed -E 's|"[^"]*/|"|' | diff -u 11-c-api/kaatuu.odotettu -
# @loppu kaatuminen

# @alku paketti
paketti:
	cd 12-paketointi && $(PYTHON) -m pip wheel --quiet --no-deps \
	    --no-build-isolation --no-index -w ../$(B)/dist .
	$(PYTHON) -m pip install --quiet --no-deps --no-index \
	    --target $(B)/asennettu $(B)/dist/nopeatarkiste-*.whl
	cd 12-paketointi && PYTHONPATH=../$(B)/asennettu \
	    $(PYTHON) -m pytest -q -p no:cacheprovider testit
	cd 12-paketointi && $(PYTHON) nayta.py ../$(B)/dist \
	    | diff -u nayta.odotettu -
	cd 12-paketointi/testit && MYPYPATH=../src mypy --strict \
	    --no-error-summary --cache-dir=/dev/null . ../nayta.py
# @loppu paketti

siivoa:
	rm -rf $(B) 12-paketointi/build 12-paketointi/src/*.egg-info
	find . -name __pycache__ -prune -exec rm -rf {} +
