# Haavoittuvuuksien analyysin esimerkit.
#
#   make         kääntää kohdeohjelmat, ajaa analyysit ja tarkistaa
#                tulosteet
#   make siivoa  poistaa build/-hakemiston
#
# Jokainen esimerkki on hakemisto NN-nimi/, jonka aja.sh kääntää
# omat ohjelmansa ja ajaa ne sanitoijien, gdb:n tai fuzzerin kanssa.
# Tulostetta verrataan tiedostoon odotettu. Ks. testaa.sh.

.PHONY: kaikki siivoa

kaikki:
	./testaa.sh

siivoa:
	rm -rf build .ruff_cache
