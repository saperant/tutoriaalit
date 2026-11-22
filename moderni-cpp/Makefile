# Moderni C++ -tutoriaali
#
#   make testaa   kääntää, ajaa ja tarkistaa kaikki esimerkit; varmistaa
#                 myös, että esimerkkien oma Makefile kääntää ne
#   make pdf      rakentaa PDF:n (vaatii pandocin ja XeLaTeXin)
#   make          molemmat: ensin testit, sitten PDF

NIMI     := moderni-cpp
YHTEISET := ../yhteiset
LUVUT    := $(sort $(wildcard luvut/*.md))
ESIMERKIT := $(shell find esimerkit -type f -not -path '*/bin/*')

.PHONY: kaikki testaa pdf siivoa

kaikki: testaa pdf

testaa:
	python3 $(YHTEISET)/testaa_esimerkit.py --kieli cpp .
	$(MAKE) -C esimerkit -s -j4
	$(MAKE) -C esimerkit -s siivoa

pdf: $(NIMI).pdf

$(NIMI).pdf: metadata.yaml $(LUVUT) $(ESIMERKIT) $(wildcard $(YHTEISET)/*)
	pandoc --defaults=$(YHTEISET)/pdf.yaml metadata.yaml $(LUVUT) -o $@

siivoa:
	rm -f $(NIMI).pdf
