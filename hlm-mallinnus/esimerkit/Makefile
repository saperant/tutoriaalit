# SystemC- ja TLM-esimerkit.
#
#   make         kääntää, ajaa ja tarkistaa kaikki esimerkit (rinnakkain
#                valitsimella -j)
#   make 08-fir  vain yksi esimerkki
#   make siivoa  poistaa build/-hakemiston
#
# Jokainen esimerkki on hakemisto NN-nimi/. Sen .cpp-tiedostot
# käännetään yhdeksi ohjelmaksi, tai hakemiston aja.sh rakentaa ja ajaa
# esimerkin itse. Tulostetta verrataan tiedostoon odotettu.
# Ks. testaa.sh.

ESIMERKIT := $(sort $(wildcard [0-9][0-9]-*))

.PHONY: kaikki skriptit siivoa $(ESIMERKIT)

kaikki: skriptit $(ESIMERKIT)
	@echo "OK: $(words $(ESIMERKIT)) esimerkkiä"

skriptit:
	shellcheck testaa.sh $(wildcard */aja.sh)

$(ESIMERKIT):
	@./testaa.sh $@

siivoa:
	rm -rf build
