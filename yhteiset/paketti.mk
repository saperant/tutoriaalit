# Tutoriaalipakettien yhteinen Makefile.
#
# Paketin oma Makefile asettaa muuttujat ja ottaa tämän tiedoston mukaan:
#
#   NIMI    := rust            # paketin hakemisto ja PDF:n nimi
#   KIELI   := rust            # testaajan kieliprofiili (useita: "sql python")
#   RAKENNE := kieli           # kieli (KIELIPAKETTI.md) tai taito
#   include ../yhteiset/paketti.mk
#
#   make testaa   tarkistaa rakenteen, testaa esimerkit ja, jos
#                 esimerkeillä on oma Makefile, varmistaa että se toimii
#   make pdf      rakentaa tutoriaalin ja pikaoppaan PDF:t
#   make          molemmat

YHTEISET  := ../yhteiset
RAKENNE   ?= kieli
LUVUT     := $(sort $(wildcard luvut/*.md))
ESIMERKIT := $(shell find esimerkit -type f -not -path '*/bin/*' \
                  -not -path '*/obj_dir/*' -not -path '*/target/*' \
                  -not -path '*/compiled/*' -not -path '*/__pycache__/*' \
                  -not -path '*/node_modules/*' -not -path '*/build/*' \
                  -not -path '*/dist/*' -not -path '*/.gradle/*' \
                  -not -path '*/test-results/*')

.PHONY: kaikki testaa pdf siivoa

kaikki: testaa pdf

testaa:
	python3 $(YHTEISET)/tarkista_paketti.py --rakenne $(RAKENNE) .
	@for kieli in $(KIELI); do \
	    python3 $(YHTEISET)/testaa_esimerkit.py --kieli $$kieli . || exit 1; \
	done
	@if [ -f esimerkit/Makefile ]; then \
	    $(MAKE) -C esimerkit -s -j4 && $(MAKE) -C esimerkit -s siivoa; \
	fi

# PDF:n korostusväri ja kansilehden alue taitopuusta (ks. korostus.py).
KOROSTUS  := $(shell python3 $(YHTEISET)/korostus.py $(NIMI))

pdf: $(NIMI).pdf $(NIMI)-pikaopas.pdf

$(NIMI).pdf: metadata.yaml $(LUVUT) $(ESIMERKIT) $(wildcard kuvat/*) \
        $(wildcard $(YHTEISET)/*)
	pandoc --defaults=$(YHTEISET)/pdf.yaml -V 'header-includes=$(KOROSTUS)' \
	    metadata.yaml $(LUVUT) -o $@

$(NIMI)-pikaopas.pdf: pikaopas.md $(ESIMERKIT) $(wildcard kuvat/*) \
        $(wildcard $(YHTEISET)/*)
	pandoc --defaults=$(YHTEISET)/pikaopas.yaml -V 'header-includes=$(KOROSTUS)' \
	    pikaopas.md -o $@

siivoa:
	rm -rf $(NIMI).pdf $(NIMI)-pikaopas.pdf .kaaviot
