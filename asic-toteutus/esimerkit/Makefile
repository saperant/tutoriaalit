# Kirjan ajoituskaaviot. Esimerkit testaa yhteinen testaaja; tämä
# Makefile tuottaa luvun 9 kellon portituksen kaavion simulaatiosta ja
# vertaa sitä tiedostoon kaaviot/portitus.json (PAIVITA=1 kirjoittaa
# sen uudelleen).
#
#   make           kaavio ja vertailu
#   make siivoa    poistaa käännöstuotteet

R      := rakennus
KAAVIO := python3 ../../yhteiset/kaaviot.py vcd

.PHONY: kaikki siivoa
kaikki: $(R)/portitus.ok

# Näytekellon rivi poistetaan ja kaavio kavennetaan: 40 nanosekunnin
# saraketta mahtuvat palstalle.
$(R)/portitus.ok: 09-portitus.sv kaaviot/jaljitys.svh kaaviot/portitus.json
	@mkdir -p $(R)
	@MAKEFLAGS= verilator --binary --timescale 1ns/100ps -Wno-fatal \
	    --top-module jaljitys -Mdir $(R)/portitus -o sim --trace \
	    09-portitus.sv kaaviot/jaljitys.svh > $(R)/portitus.loki 2>&1 \
	    || { cat $(R)/portitus.loki; false; }
	@$(R)/portitus/sim > /dev/null
	@$(KAAVIO) $(R)/portitus.vcd --kello nayte --jaksot 40 \
	    --signaalit t.clk=clk,t.sallinta=sallinta,t.gclk_and=gclk_and,\
	t.gclk_icg=gclk_icg > $(R)/portitus.raaka.json
	@rm -f $(R)/portitus.vcd
	@python3 -c 'import json, sys; k = json.load(sys.stdin); \
	    k["signal"] = k["signal"][1:]; k["config"] = {"hscale": 0.4}; \
	    json.dump(k, sys.stdout, ensure_ascii=False, indent=1)' \
	    < $(R)/portitus.raaka.json > $(R)/portitus.json
	@if [ "$(PAIVITA)" = 1 ]; then cp $(R)/portitus.json kaaviot/; fi
	@diff -u kaaviot/portitus.json $(R)/portitus.json
	@echo "OK: kaavio portitus"
	@touch $@

siivoa:
	rm -rf $(R)
