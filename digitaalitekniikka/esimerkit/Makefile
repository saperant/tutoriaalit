# Ajoituskaaviot simulaatiosta.
#
# Kirjan ajoituskaaviot ovat tiedostoja kaaviot/*.json. Tämä Makefile
# tuottaa ne uudelleen simuloimalla esimerkit ja vertaa tulosta
# tallennettuun, joten kaavio ei voi erkaantua koodista.
#
#   make           tarkistaa kaaviot (ajetaan osana make testaa)
#   make paivita   kirjoittaa kaaviot/*.json uudelleen
#   make siivoa    poistaa käännöstuotteet
#
# Simuloitavan kaavion kuvaus on tiedostossa kaaviot/<nimi>.kaavio: se on
# SystemVerilog-kääre, joka instansioi esimerkin testipenkin, tuo
# näytettävät signaalit omiksi johdoikseen ja kirjoittaa VCD-tiedoston.
# Otsakerivit kertovat lähteet ja kaaviot.py:n valitsimet:
#
#   // lahde: 09-laskurit.sv
#   // vcd: --kello clk --signaalit sarja,q0 --jaksot 9

KAAVIOT := $(abspath ../../yhteiset/kaaviot.py)
RAK     := build
SIMULOIDUT := $(patsubst kaaviot/%.kaavio,%,$(wildcard kaaviot/*.kaavio))
TARKISTUKSET := $(SIMULOIDUT:%=$(RAK)/%.ok) $(RAK)/07-hasardi.ok

.PHONY: kaikki paivita siivoa
kaikki: $(TARKISTUKSET)

# Kaavio simuloidaan Verilatorilla omassa hakemistossaan.
$(RAK)/%.json: kaaviot/%.kaavio $(wildcard *.sv */*.sv) $(KAAVIOT)
	@rm -rf $(RAK)/$* && mkdir -p $(RAK)/$*
	@cp $< $(RAK)/$*/kaavio.sv
	@lahteet=$$(sed -n 's#^// lahde: ##p' $<); \
	verilator --binary --trace --top-module kaavio -Wno-fatal \
	    -Mdir $(RAK)/$*/obj -o sim $$lahteet $(RAK)/$*/kaavio.sv \
	    > $(RAK)/$*/verilator.log 2>&1 \
	    || { cat $(RAK)/$*/verilator.log; exit 1; }
	@cd $(RAK)/$* && timeout 120 ./obj/sim > sim.log \
	    || { echo "kaavion $* simulointi epäonnistui"; exit 1; }
	@python3 $(KAAVIOT) vcd $(RAK)/$*/kaavio.vcd \
	    $$(sed -n 's#^// vcd: ##p' $<) > $@

# Hasardikaavio tulee porttisimulaattorin tulosteesta (aikayksikkö per
# merkki): alkuperäinen multiplekseri ja konsensustermillä korjattu lähtö.
$(RAK)/07-hasardi.json: 07-hasardi.odotettu
	@mkdir -p $(RAK)
	@python3 -c 'import json, sys; \
	osat = open(sys.argv[1]).read().split("\n\n"); \
	rivit = lambda o: dict(r.split() for r in o.splitlines()[1:]); \
	a, k = rivit(osat[0]), rivit(osat[1]); \
	aalto = lambda b: "".join(c if i == 0 or c != b[i - 1] else "." \
	    for i, c in enumerate(b)); \
	s = [{"name": n, "wave": aalto(a[n])} for n in ("s", "s_n", "t0", "t1")]; \
	s += [{"name": "y", "wave": aalto(a["y"])}, \
	      {"name": "y + ab", "wave": aalto(k["y"])}]; \
	print(json.dumps({"signal": s}, ensure_ascii=False))' $< > $@

$(RAK)/%.ok: $(RAK)/%.json kaaviot/%.json
	@diff -u kaaviot/$*.json $< \
	    || { echo "kaavio $* ei vastaa simulaatiota: make paivita"; exit 1; }
	@touch $@

paivita: $(SIMULOIDUT:%=$(RAK)/%.json) $(RAK)/07-hasardi.json
	@for k in $(SIMULOIDUT) 07-hasardi; do \
	    cp $(RAK)/$$k.json kaaviot/$$k.json; done

siivoa:
	rm -rf $(RAK)
