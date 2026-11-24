# Takaisinmallinnuksen esimerkit.
#
#   make         rakentaa kohdeohjelmat, ajaa analyysit ja tarkistaa
#                tulosteet
#   make siivoa  poistaa build/-hakemiston
#
# Jokainen esimerkki on hakemisto NN-nimi/, jonka aja.sh kääntää
# kohdeohjelman ja ajaa sille analyysit. Tulostetta verrataan
# tiedostoon odotettu. Ks. testaa.sh.

.PHONY: kaikki siivoa

kaikki:
	./testaa.sh

siivoa:
	rm -rf build .ruff_cache
