# Moderni C++ -tutoriaali
#
#   make testaa   tarkistaa kielipaketin rakenteen (yhteiset/KIELIPAKETTI.md),
#                 kääntää, ajaa ja tarkistaa kaikki esimerkit ja varmistaa,
#                 että esimerkkien oma Makefile kääntää ne
#   make pdf      rakentaa PDF:n ja pikaoppaan (vaatii pandocin ja XeLaTeXin)
#   make          molemmat: ensin testit, sitten PDF

NIMI     := moderni-cpp
YHTEISET := ../yhteiset
LUVUT    := $(sort $(wildcard luvut/*.md))
ESIMERKIT := $(shell find esimerkit -type f -not -path '*/bin/*')

.PHONY: kaikki testaa pdf siivoa

kaikki: testaa pdf

testaa:
	python3 $(YHTEISET)/tarkista_paketti.py .
	python3 $(YHTEISET)/testaa_esimerkit.py --kieli cpp .
	$(MAKE) -C esimerkit -s -j4
	$(MAKE) -C esimerkit -s siivoa

pdf: $(NIMI).pdf $(NIMI)-pikaopas.pdf

$(NIMI).pdf: metadata.yaml $(LUVUT) $(ESIMERKIT) $(wildcard $(YHTEISET)/*)
	pandoc --defaults=$(YHTEISET)/pdf.yaml metadata.yaml $(LUVUT) -o $@

$(NIMI)-pikaopas.pdf: pikaopas.md $(ESIMERKIT) $(wildcard $(YHTEISET)/*)
	pandoc --defaults=$(YHTEISET)/pikaopas.yaml pikaopas.md -o $@

siivoa:
	rm -f $(NIMI).pdf $(NIMI)-pikaopas.pdf
