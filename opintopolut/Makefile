# Opintopolut: taitopuu, roolipolut ja tutoriaalien tuotantosuunnitelma.
#
#   make testaa   tarkistaa taitopuun ja että README on ajan tasalla
#   make readme   generoi README.md:n taitopuu.toml-tiedostosta
#   make pdf      generoi luvut ja kaaviot ja rakentaa PDF:n
#   make          testit ja PDF

NIMI     := opintopolut
YHTEISET := ../yhteiset
RAKENNUS := rakennus
TAITOPUU := python3 $(YHTEISET)/taitopuu.py

.PHONY: kaikki testaa readme pdf siivoa

kaikki: testaa pdf

testaa:
	$(TAITOPUU) tarkista taitopuu.toml --readme README.md

readme:
	$(TAITOPUU) tarkista taitopuu.toml --readme README.md --kirjoita-readme

pdf: $(NIMI).pdf

$(NIMI).pdf: taitopuu.toml metadata.yaml ../VISIO.md $(wildcard luvut/*.md) \
             $(wildcard $(YHTEISET)/*)
	rm -rf $(RAKENNUS)
	$(TAITOPUU) generoi taitopuu.toml $(RAKENNUS)
	pandoc --defaults=$(YHTEISET)/pdf.yaml metadata.yaml \
	    ../VISIO.md luvut/01-johdanto.md $(RAKENNUS)/luvut/*.md \
	    luvut/06-yllapito.md -o $@

siivoa:
	rm -rf $(RAKENNUS) $(NIMI).pdf
