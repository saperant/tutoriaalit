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

kaikki: skriptit $(ESIMERKIT) kaaviot
	@echo "OK: $(words $(ESIMERKIT)) esimerkkiä"

# Kirjan ajoituskaaviot verrataan hakemiston kaaviot/ tiedostoihin;
# PAIVITA=1 kirjoittaa ne uudelleen.
#   laskuri.json    01-laskurin simulaatio VCD:nä (kaaviot/laskuri.cpp)
#   at-vaiheet.json 13-at:n vaiheloki (kaaviot/at_vaiheet.py)
KAAVIOTYOKALU := $(abspath ../../yhteiset/kaaviot.py)
KR := build/kaaviot
.PHONY: kaaviot
kaaviot:
	@mkdir -p $(KR)
	@$${CXX:-g++-14} -std=c++17 -O1 -Wall -Wextra -Werror \
	    kaaviot/laskuri.cpp $$(pkg-config --cflags --libs systemc tlm) \
	    -o $(KR)/laskuri
	@cd $(KR) && SC_COPYRIGHT_MESSAGE=DISABLE timeout 60 ./laskuri \
	    > /dev/null
	@python3 $(KAAVIOTYOKALU) vcd $(KR)/kaavio.vcd --kello clk \
	    --signaalit nollaus,laske,arvo,ylivuoto --jaksot 22 --kanta d \
	    --alkureuna > $(KR)/laskuri.json
	@python3 kaaviot/at_vaiheet.py 13-at/odotettu > $(KR)/at-vaiheet.json
	@for k in laskuri.json at-vaiheet.json; do \
	    if [ "$(PAIVITA)" = 1 ]; then cp $(KR)/$$k kaaviot/$$k; fi; \
	    diff -u kaaviot/$$k $(KR)/$$k \
	        || { echo "kaavio $$k ei vastaa (PAIVITA=1)"; exit 1; }; \
	done

skriptit:
	shellcheck testaa.sh $(wildcard */aja.sh)

$(ESIMERKIT):
	@./testaa.sh $@

siivoa:
	rm -rf build
