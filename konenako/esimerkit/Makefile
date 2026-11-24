# Esimerkit, joita yhteinen testaaja ei aja:
#
#   make           pytest-testit hakemistoesimerkeissä (test_*.py) ja
#                  C++-esimerkki (OpenCV 4 Ubuntun paketista, pkg-config)
#   make siivoa    poistaa välimuistit ja käännöstuotteet
#
# Yksittäinen testi ajetaan esimerkiksi näin:
#   cd 07-kalibrointi && python3 -m pytest -q -k kulmat

TESTIT := $(sort $(patsubst %/,%,$(dir $(wildcard */test_*.py))))
export PYTHONDONTWRITEBYTECODE := 1
PYTEST := python3 -m pytest -q -p no:cacheprovider

# C++: varoitukset virheinä ja sanitoijat. OpenCV:n otsakkeet otetaan
# -isystem-polusta, jotta kirjaston omat varoitukset eivät kaada käännöstä.
KAANTAJAT := g++-14 clang++-20
CXXFLAGS  := -std=c++20 -Wall -Wextra -Wpedantic -Werror -g \
             -fsanitize=address,undefined -fno-sanitize-recover=all
OPENCV_CFLAGS = $(subst -I,-isystem ,$(shell pkg-config --cflags opencv4))
OPENCV_LIBS   = $(shell pkg-config --libs opencv4)

.PHONY: kaikki siivoa cpp $(TESTIT)

kaikki: $(TESTIT) cpp

$(TESTIT):
	cd $@ && $(PYTEST)

cpp:
	@pkg-config --exists opencv4 || \
	    { echo "OpenCV:n C++-kirjasto puuttuu (libopencv-dev)"; exit 1; }
	@mkdir -p cpp/bin
	@for k in $(KAANTAJAT); do \
	    $$k $(CXXFLAGS) $(OPENCV_CFLAGS) cpp/reunat.cpp $(OPENCV_LIBS) \
	        -o cpp/bin/reunat-$$k || exit 1; \
	    ./cpp/bin/reunat-$$k > cpp/bin/reunat-$$k.tuloste || exit 1; \
	    diff -u cpp/reunat.odotettu cpp/bin/reunat-$$k.tuloste || exit 1; \
	done
	@echo "OK: C++-esimerkki ($(KAANTAJAT))"

siivoa:
	rm -rf cpp/bin
	find . -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache \
	    | xargs rm -rf
