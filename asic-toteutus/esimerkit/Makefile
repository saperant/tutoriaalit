# Kirjan ajoituskaaviot. Esimerkit testaa yhteinen testaaja; tämä
# Makefile tuottaa luvun 6 scan-testin ja luvun 9 kellon portituksen
# kaaviot simulaatiosta ja vertaa niitä tiedostoihin kaaviot/*.json
# (PAIVITA=1 kirjoittaa ne uudelleen).
#
#   make           kaavio ja vertailu
#   make siivoa    poistaa käännöstuotteet

R      := rakennus
KAAVIO := python3 ../../yhteiset/kaaviot.py vcd

.PHONY: kaikki siivoa
kaikki: $(R)/portitus.ok $(R)/scan.ok

# Scan-testi: netlistan tulostaa esimerkki 06-scan.py (argumentti
# netlista), ja testipenkki tp_scan.v tallentaa jäljen valitsimella
# +vcd. Kaaviossa on koko testijakso: 8 siirtoa, kaappaus ja 8 siirtoa.
$(R)/scan.ok: 06-scan.py synteesi.py laskuri.v tp_scan.v opetus_solut.v \
    opetus.lib kaaviot/scan.json
	@mkdir -p $(R)
	@python3 06-scan.py netlista > $(R)/scan.v
	@iverilog -o $(R)/scan.sim $(R)/scan.v opetus_solut.v tp_scan.v
	@cd $(R) && vvp -n scan.sim +vcd > /dev/null
	@$(KAAVIO) $(R)/scan.vcd --kello tp.clk --jaksot 17 --kanta h \
	    --signaalit tp.scan_en=scan_en,tp.scan_in=scan_in,tp.q=q,\
	tp.scan_out=scan_out > $(R)/scan.json
	@rm -f $(R)/scan.vcd
	@if [ "$(PAIVITA)" = 1 ]; then cp $(R)/scan.json kaaviot/; fi
	@diff -u kaaviot/scan.json $(R)/scan.json
	@echo "OK: kaavio scan"
	@touch $@

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
