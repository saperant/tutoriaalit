# Laiteohjelmiston takaisinmallinnuksen esimerkit.
#
#   make         rakentaa laitteen (laite/), ajaa analyysit ja tarkistaa
#                tulosteet
#   make siivoa  poistaa build/-hakemiston
#
# Jokainen esimerkki on hakemisto NN-nimi/, jonka aja.sh ajaa
# analyysin laitteen tuotteille. Tulostetta verrataan tiedostoon
# odotettu. Ks. testaa.sh.

.PHONY: kaikki siivoa

kaikki:
	./testaa.sh

siivoa:
	rm -rf build .ruff_cache
